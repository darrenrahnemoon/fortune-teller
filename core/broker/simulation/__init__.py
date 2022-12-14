from core.chart.group import ChartGroup
import logging
import typing
import pandas
import random
from dataclasses import dataclass, field

from core.broker.broker import Broker
from core.broker.simulation.report import BacktestReport
from core.broker.simulation.scheduler import Scheduler
from core.broker.simulation.repository import SimulationRepository

if typing.TYPE_CHECKING:
	from core.strategy import Strategy
from core.order import Order, OrderStatus, OrderType
from core.position import Position, PositionStatus, PositionType
from core.chart import Chart, CandleStickChart, Symbol

from core.interval import Interval
from core.utils.time import TimeWindow, normalize_timestamp, TimestampLike
from core.utils.collection import ensure_list

logger = logging.getLogger(__name__)

@dataclass
class SimulationBroker(Broker):
	scheduler: Scheduler = field(default_factory=Scheduler, init=False, repr=False)

	_timesteps: pandas.DatetimeIndex = field(init=False, repr=False)
	equity_curve: pandas.Series = field(init=False, repr=False)

	initial_cash: float = 1000.
	leverage: float = 1.
	latency: Interval = Interval.Millisecond(2)

	positions: list[Position] = field(default_factory=list, init=False, repr=False)
	orders: list[Order] = field(default_factory=list, init=False, repr=False)

	@classmethod
	@property
	def repository(self):
		return SimulationRepository()

	def __post_init__(self):
		self._now = None

	@property
	def timesteps(self):
		return self._timesteps

	@timesteps.setter
	def timesteps(self, value: Chart or pandas.DatetimeIndex):
		if isinstance(value, Chart):
			records = self.repository.read_chart_raw(value)
			self._timesteps = pandas.DatetimeIndex([ record[Chart.timestamp_field] for record in records ])
		else:
			self._timesteps = value
		if type(self._timesteps) == pandas.DatetimeIndex:
			self.equity_curve = pandas.Series(index=self._timesteps, dtype='float', name='equity')

	@property
	def now(self) -> pandas.Timestamp:
		return self._now or super().now

	@now.setter
	def now(self, value: TimestampLike):
		self._now = normalize_timestamp(value)

	def read_chart(self, chart: Chart):
		self.ensure_timestamp(chart)
		self.repository.read_chart(chart)

	def write_chart(self, chart: Chart):
		self.repository.write_chart(chart)

	@classmethod
	def remove_historical_data(self, chart: Chart):
		self.repository.drop_collection_for_chart(chart)

	@classmethod
	def get_common_time_window(self, chart_group: ChartGroup) -> TimeWindow:
		from_timestamp = []
		to_timestamp = []
		for chart in chart_group.charts:
			from_timestamp.append(self.get_min_available_timestamp_for_chart(chart))
			to_timestamp.append(self.get_max_available_timestamp_for_chart(chart))
		return TimeWindow(max(from_timestamp), min(to_timestamp))

	@classmethod
	def get_available_charts(self, filter = {}, include_timestamps = False) -> list[Chart]:
		return self.repository.get_available_charts(filter=filter, include_timestamps=include_timestamps)

	@classmethod
	def get_max_available_timestamp_for_chart(self, chart: Chart) -> pandas.Timestamp:
		return self.repository.get_max_available_timestamp_for_chart(chart)

	@classmethod
	def get_min_available_timestamp_for_chart(self, chart: Chart) -> pandas.Timestamp:
		return self.repository.get_min_available_timestamp_for_chart(chart)

	def backtest(self, strategy: 'Strategy'):
		for self.now in self.timesteps:
			self.scheduler.run_as_of(self.now)

			for order in self.get_orders(status='open'):
				price = self.get_last_price(order.symbol)
				if (order.type == 'long' and order.stop and price >= order.stop) \
					or (order.type == 'short' and order.stop and price <= order.stop):
					order.stop = None
				if order.stop == None \
					and (order.is_market_order \
						or (order.type == 'long' and order.limit and order.limit <= price)\
						or (order.type == 'short' and order.limit and order.limit >= price)
					):
					self.fill_order(order)

			for position in self.get_positions(status='open'):
				price = self.get_last_price(position.symbol)
				if (
					position.type == 'long' and (
						(position.sl and price <= position.sl) or 
						(position.tp and price >= position.tp)
					)
					) or (
					position.type == 'short' and (
						(position.sl and price >= position.sl) or 
						(position.tp and price <= position.tp)
					)
				):
					self.close_position(position, price=price)
			strategy.handler()
			self.equity_curve[self.now] = self.equity

		report = BacktestReport.from_strategy(strategy)
		self.repository.write_backtest_report(report)

	def get_last_price(self, symbol: Symbol) -> float:
		data = self.repository.read_chart_raw(
			CandleStickChart(symbol=symbol, interval=Interval.Minute(1), count=1),
		)[0]
		return data['close']

	def get_orders(
		self,
		symbol: Symbol = None,
		type: OrderType = None,
		from_timestamp: TimestampLike = None,
		to_timestamp: TimestampLike = None,
		status: OrderStatus = None, 
	) -> list[Order]:
		status = ensure_list(status)
		from_timestamp = normalize_timestamp(from_timestamp)
		to_timestamp = normalize_timestamp(to_timestamp or self.now)
		return [
			order
			for order in self.orders
			if ((not symbol) or order.symbol == symbol) \
				and ((not from_timestamp) or order.open_timestamp >= from_timestamp) \
				and ((not to_timestamp) or order.open_timestamp <= to_timestamp)
				and ((not status) or order.status in status)
				and ((not type) or order.type == type)
		]

	def get_positions(
		self,
		symbol: Symbol = None,
		type: PositionType = None,
		from_timestamp: TimestampLike = None,
		to_timestamp: TimestampLike = None,
		status: PositionStatus = None,
	) -> list[Position]:
		status = ensure_list(status)
		from_timestamp = normalize_timestamp(from_timestamp)
		to_timestamp = normalize_timestamp(to_timestamp or self.now)
		return [
			position
			for position in self.positions
			if ((not symbol) or position.symbol == symbol) \
				and ((not from_timestamp) or position.open_timestamp >= from_timestamp) \
				and ((not to_timestamp) or position.open_timestamp <= to_timestamp)
				and ((not status) or position.status in status)
				and ((not type) or position.type == type)
		]

	def place_order(self, order: Order, schedule=True) -> Order:
		if schedule:
			self.schedule_action(self.place_order, order, schedule=False)
			return

		if order.id != None:
			logger.warn(f'Order is already placed: {order}')
			return

		order.id = random.randint(0, 1000000000)
		order.status = 'open'
		order.open_timestamp = order.broker.now
		self.orders.append(order)
		return order

	def cancel_order(self, order: Order, schedule=True):
		if schedule:
			self.schedule_action(self.cancel_order, order, schedule=False)
			return

		if order.status == 'filled':
			logger.warning(f'Cannot cancel an order that has been filled: {order}')
			return

		order.status = 'cancelled'
		order.close_timestamp = self.now

	def fill_order(self, order: Order):
		if order.status != 'open':
			logger.warn(f"Cannot fill an order with status '{order.status}': {order}")
			return

		order.position = Position(
			id = random.randint(0, 1000000000),
			broker = self,
			symbol = order.symbol,
			type = order.type,
			size = order.size,
			entry_price = self.get_last_price(order.symbol),
			open_timestamp = self.now,
			tp = order.tp,
			sl = order.sl,
			status = 'open',
			order = order,
		)
		order.status = 'filled'
		order.close_timestamp = self.now
		self.positions.append(order.position)
		return order.position

	def close_position(self, position: Position, schedule=True):
		if schedule:
			self.schedule_action(self.close_position, position, schedule=False)
			return

		if position.status == 'closed':
			logger.warning(f'Cannot close a position that is already closed: {position}')
			return

		position.status = 'closed'
		position.close_timestamp = self.now
		position.exit_price = self.get_last_price(position.symbol)

	def schedule_action(
		self,
		action: typing.Callable,
		*args,
		**kwargs,
	):
		self.scheduler.add(
			action = action,
			timestamp = self.now + self.latency.to_pandas_timedelta(),
			args = args,
			kwargs = kwargs
		)

	@property
	def balance(self) -> float:
		return self.initial_cash + sum(position.profit for position in self.get_positions(status='closed'))

	@property
	def equity(self) -> float:
		return self.initial_cash + sum(position.profit for position in self.get_positions())

	@property
	def leverage(self) -> float:
		return self._leverage

	@leverage.setter
	def leverage(self, value: float):
		self._leverage = value
