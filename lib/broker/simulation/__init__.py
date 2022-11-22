import logging
import typing
import pandas
import random

from lib.broker.broker import Broker
from lib.broker.simulation.scheduler import Scheduler
from lib.broker.simulation.repository import Repository

from lib.order import Order
from lib.position import Position
from lib.chart import Chart

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
		from_timestamp: pandas.Timestamp or str = None,
		to_timestamp: pandas.Timestamp or str = None,
		trigger: Chart or Interval = None,
		initial_cash: float = 1000.,
		leverage: float = 1.,
		latency: Interval = Interval.Millisecond(1),
	):
		# Time progression parameters
		self.now = None
		self.from_timestamp = normalize_timestamp(from_timestamp)
		self.to_timestamp = normalize_timestamp(to_timestamp)
		if isinstance(trigger, Chart):
			records = self.repository.read(trigger)
			self.timesteps = pandas.DatetimeIndex([ record['timestamp'] for record in records ])
		elif isinstance(trigger, Interval):
			self.timesteps = pandas.date_range(self.from_timestamp, self.to_timestamp, freq=trigger.to_pandas_frequency(), name='timesteps')
		else:
			logger.critical(f'Invalid trigger for backtesting: {trigger}')

		self.latency = latency
		self.scheduler = Scheduler()

		self.leverage = float(leverage)
		self.initial_cash = float(initial_cash)
		self.equity_curve = pandas.Series(index=self.timesteps, dtype='float', name='equity')

		self.positions: list[Position] = []
		self.orders: list[Order] = []

		for self.now in self.timesteps:
			self.scheduler.run_as_of(self.now)

			# Reduce db calls by caching this iteration's last prices
			last_prices = dict()

			for order in self.get_orders(status='open'):
				price = last_prices[order.symbol] = last_prices[order.symbol] if order.symbol in last_prices else self.get_last_price(order.symbol)
				if (order.type == 'long' and price >= order.stop) \
					or (order.type == 'short' and price <= order.stop):
					order.stop = None
				if order.stop == None \
					and (order.is_market_order \
						or (order.type == 'long' and order.limit and order.limit <= price)\
						or (order.type == 'short' and order.limit and order.limit >= price)
					):
					self.fill_order(order)

			for position in self.get_positions(status='open'):
				price = last_prices[position.symbol] = last_prices[position.symbol] if position.symbol in last_prices else self.get_last_price(position.symbol)
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
				try:
					if not strategy.is_aborted:
						strategy.handler()
				except Exception as exception:
					logger.error(f'Strategy {strategy} encountered an exception. Safely continuing...\n{exception}')
			self.equity_curve[self.now] = self.equity

	@property
	def now(self) -> pandas.Timestamp:
		return self._now or super().now

	@now.setter
	def now(self, value: pandas.Timestamp):
		self._now = value

	def get_last_price(self, symbol: str) -> float:
		pass
		# query = select(Tick.bid, Tick.ask)\
		# 	.where(Tick.symbol == symbol)\
		# 	.where(Tick.timestamp <= self.now)\
		# 	.order_by(Tick.timestamp.desc())\
		# 	.limit(1)
		# print(f'{query.compile()} {query.compile().params}')
		# result = database.engine.execute(query).fetchone()
		# return (result[0] + result[1]) / 2

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
			if (symbol and order.symbol == symbol) \
				or (from_timestamp and order.open_timestamp >= from_timestamp) \
				or (to_timestamp and order.close_timestamp >= to_timestamp)
				or (status and order.status in status)
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
			if (symbol and position.symbol == symbol) \
				or (from_timestamp and position.open_timestamp >= from_timestamp) \
				or (to_timestamp and position.close_timestamp >= to_timestamp)
				or (status and position.status in status)
		]

	def place_order(self, order: Order) -> Order:
		if order.id != None:
			logger.warn(f'Order is already placed: {order}')
			return

		order.id = random.randint(0, 1000000000)
		order.status = 'open'
		order.open_timestamp = order.broker.now
		self.orders.append(order)
		return order

	def fill_order(self, order: Order):
		if order.status != 'open':
			logger.warn(f"Cannot fill an order with status '{order.status}': {order}")
			return

		order.position = Position(
			id=random.randint(0, 1000000000),
			broker=self,
			symbol=order.symbol,
			position_type=order.type,
			size=order.size,
			entry_price=self.get_last_price(order.symbol),
			entry_timestamp=self.now,
			tp=order.tp,
			sl=order.sl,
			order=order
		)
		order.status = 'filled'
		order.close_timestamp = self.now
		self.positions.append(order.position)
		return order.position

	def cancel_order(self, order: Order):
		if order.status == 'filled':
			logger.warning(f'Cannot cancel an order that has been filled: {order}')
			return

		order.status = 'cancelled'
		order.close_timestamp = self.now

	def close_position(self, position: Position, price=None):
		if position.status == 'closed':
			logger.warning(f'Cannot close a position that is already closed: {position}')
			return

		position.exit_timestamp = self.now
		position.exit_price = price or self.get_last_price(position.symbol)

	def call_with_latency(
		self,
		action: typing.Callable,
		*args,
		**kwargs,
	):
		self.scheduler.add(
			action=action,
			timestamp=self.now + self.latency,
			*args,
			**kwargs
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
