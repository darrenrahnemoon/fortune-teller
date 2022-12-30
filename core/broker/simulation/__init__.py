import logging
import typing
import pandas
import random
from dataclasses import dataclass, field

from core.broker.broker import Broker
from .report import BacktestReport
from .scheduler import Scheduler

if typing.TYPE_CHECKING:
	from core.strategy import Strategy
from core.order import Order, OrderStatus, OrderType
from core.position import Position, PositionStatus, PositionType
from core.chart import Chart, CandleStickChart, Symbol
from core.repository import SimulationRepository
from .serializers import DataClassMongoDocumentSerializer

from core.interval import Interval
from core.utils.time import normalize_timestamp, TimestampLike
from core.utils.collection import ensure_list

logger = logging.getLogger(__name__)

@dataclass
class SimulationBroker(Broker):
	dataclass_serializer = DataClassMongoDocumentSerializer()

	initial_cash: float = 1000.
	latency: Interval = Interval.Millisecond(2)
	positions: list[Position] = field(default_factory = list, repr = False)
	orders: list[Order] = field(default_factory = list, repr = False)

	scheduler: Scheduler = field(default_factory = Scheduler)
	repository: SimulationRepository = field(default_factory = SimulationRepository)

	def __post_init__(self):
		self._now = None
		self._timesteps: pandas.DatetimeIndex = None
		self.equity_curve: pandas.Series = None

	def get_last_price(self, symbol: Symbol) -> float:
		chart = CandleStickChart(
			symbol = symbol,
			interval = Interval.Minute(1),
			count = 1,
			to_timestamp = self.now,
			repository = self.repository
		).read()
		return chart.data['close'].iloc[0]

	@property
	def timesteps(self):
		return self._timesteps

	@timesteps.setter
	def timesteps(self, value: Chart or pandas.DatetimeIndex):
		if isinstance(value, Chart):
			records = self.repository.read_chart(value, select = [])
			self._timesteps = records.index
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
		self.write_backtest_report(report)

	def write_backtest_report(self, report: BacktestReport):
		collection = self.backtest_reports.get_collection(type(report.strategy).__name__)
		serialized_report = self.serializers.dataclass.to_mongo_document(report)
		collection.insert_one(serialized_report)

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

	def place_order(self, order: Order, schedule = True) -> Order:
		if schedule:
			self.schedule_action(self.place_order, order, schedule = False)
			return

		if order.id != None:
			logger.warn(f'Order is already placed: {order}')
			return

		order.id = random.randint(0, 1000000000)
		order.status = 'open'
		order.open_timestamp = order.broker.now
		self.orders.append(order)
		return order

	def cancel_order(self, order: Order, schedule = True):
		if schedule:
			self.schedule_action(self.cancel_order, order, schedule = False)
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

	def close_position(self, position: Position, schedule = True):
		if schedule:
			self.schedule_action(self.close_position, position, schedule = False)
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
	def backtest_reports(self):
		return self.client['backtest_reports']