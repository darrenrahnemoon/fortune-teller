from lib.chart.candlestick import CandleStickChart
import logging
import typing
import pandas
import random

from lib.broker.broker import Broker
from lib.broker.simulation.scheduler import Scheduler
from lib.broker.simulation.repository import Repository

from lib.order import Order
from lib.position import Position
from lib.chart import Chart, TickChart

from lib.interval import Interval
from lib.utils.time import normalize_timestamp
from lib.utils.collection import ensure_list

logger = logging.getLogger(__name__)

class SimulationBroker(Broker):
	def __init__(
		self,
		repository: Repository = Repository(),
		**kwargs
	) -> None:
		super().__init__(**kwargs)
		self.repository = repository

	def read(self, chart: Chart):
		self.ensure_timestamp(chart)
		records = self.repository.read(chart)
		dataframe = pandas.DataFrame.from_records(records, columns=[ 'timestamp' ] + chart.value_fields)
		chart.load_dataframe(dataframe)
		return chart

	def write(self, chart: Chart):
		data = chart.data
		if len(data) == 0:
			logger.warn(f'Attempted to write an empty {chart} into database. Skipping...')
			return

		self.repository.write(chart)
		return chart

	def remove_historical_data(self, chart: Chart):
		self.repository.drop_collection_for(chart)

	def get_max_timestamp(self, chart: Chart) -> pandas.Timestamp:
		return self.repository.get_max_timestamp(chart)

	def get_min_timestamp(self, chart: Chart) -> pandas.Timestamp:
		return self.repository.get_min_timestamp(chart)

	def backtest(
		self,
		chart: Chart,
		initial_cash: float = 1000.,
		leverage: float = 1.,
		latency: Interval = Interval.Millisecond(2),
	):
		records = self.repository.read(chart)
		self.timesteps = pandas.DatetimeIndex([ record['timestamp'] for record in records ])
		del records # free up memory since this variable can potentially be huge

		self.latency = latency
		self.scheduler = Scheduler()

		self.leverage = float(leverage)
		self.initial_cash = float(initial_cash)
		self.equity_curve = pandas.Series(index=self.timesteps, dtype='float', name='equity')

		self.positions: list[Position] = []
		self.orders: list[Order] = []

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
			for strategy in self.strategies:
				if not strategy.is_aborted:
					strategy.handler()
			self.equity_curve[self.now] = self.equity

	@property
	def now(self) -> pandas.Timestamp:
		return self._now or super().now

	@now.setter
	def now(self, value: pandas.Timestamp):
		self._now = normalize_timestamp(value)

	def get_last_price(self, symbol: str) -> float:
		tick = self.repository.read(
			# TickChart(symbol=symbol, to_timestamp=self.now),
			CandleStickChart(symbol=symbol, interval=Interval.Minute(1), to_timestamp=self.now),
			limit=1,
		)[0]
		return tick['close']
		# return (tick['bid'] + tick['ask']) / 2

	def get_orders(
		self,
		symbol: str = None,
		from_timestamp: pandas.Timestamp = None,
		to_timestamp: pandas.Timestamp = None,
		status: str = None, 
	) -> list[Order]:
		status = ensure_list(status)
		to_timestamp = to_timestamp or self.now
		return [
			order
			for order in self.orders
			if ((not symbol) or order.symbol == symbol) \
				and ((not from_timestamp) or order.open_timestamp >= from_timestamp) \
				and ((not to_timestamp) or order.open_timestamp <= to_timestamp)
				and ((not status) or order.status in status)
		]

	def get_positions(
		self,
		symbol: str = None,
		from_timestamp: pandas.Timestamp = None,
		to_timestamp: pandas.Timestamp = None,
		status: str = None, 
	) -> list[Order]:
		status = ensure_list(status)
		to_timestamp = to_timestamp or self.now
		return [
			position
			for position in self.positions
			if ((not symbol) or position.symbol == symbol) \
				and ((not from_timestamp) or position.open_timestamp >= from_timestamp) \
				and ((not to_timestamp) or position.open_timestamp <= to_timestamp)
				and ((not status) or position.status in status)
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
			id=random.randint(0, 1000000000),
			broker=self,
			symbol=order.symbol,
			type=order.type,
			size=order.size,
			entry_price=self.get_last_price(order.symbol),
			open_timestamp=self.now,
			tp=order.tp,
			sl=order.sl,
			order=order
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

		position.close_timestamp = self.now
		position.exit_price = self.get_last_price(position.symbol)

	def schedule_action(
		self,
		action: typing.Callable,
		*args,
		**kwargs,
	):
		self.scheduler.add(
			action=action,
			timestamp=self.now + self.latency.to_pandas_timedelta(),
			args=args,
			kwargs=kwargs
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
