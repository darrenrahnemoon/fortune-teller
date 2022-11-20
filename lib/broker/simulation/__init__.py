from inspect import isclass
import typing
import numpy
import pandas
import random

from lib.broker.broker import Broker
from lib.broker.simulation.scheduler import Scheduler

from lib.order import Order
from lib.position import Position
from lib.strategy import Strategy
from lib.chart import Chart

from lib.interval import Interval
from lib.utils.time import normalize_timestamp
from lib.utils.collection import ensure_list

class SimulationBroker(Broker):
	def read(self, chart: Chart):
		self.ensure_timestamp(chart)
		logger = self.logger.getChild('read')
		logger.info(f'Reading {chart} from database...')
		query = select(*[ getattr(chart.model, key) for key in chart.value_fields ])\
			.where(*[ getattr(chart.model, key) == getattr(chart, key) for key in chart.query_fields ])\
			.where(chart.model.timestamp.between(chart.from_timestamp, chart.to_timestamp))
		compiled_query = query.compile()
		logger.debug(f'Query:\n{compiled_query}\n\nParams:\n{compiled_query.params}')
		result = database.engine.execute(query).all()
		logger.debug(f'Converting records to dataframe. Row sample:\n{result[0] if len(result) else None}')
		dataframe = pandas.DataFrame.from_records(result, columns=chart.value_fields)
		logger.debug(f'Converted dataframe: \n{dataframe}')
		chart.load_dataframe(dataframe)
		logger.info(f'Successfully read {chart} from database.')
		return chart

	def write(self, chart: Chart, batch_size=1000):
		logger = self.logger.getChild('write')
		data = chart.data
		if len(data) == 0:
			logger.warn(f'Attempted to write an empty {chart} into database. Aborting...')
			return

		logger.info(f'Writing {chart} to database...')
		query_fields = { key: getattr(chart, key) for key in chart.query_fields }
		batch_count = int(len(data) / batch_size) or 1
		batches = numpy.array_split(data, batch_count)
		logger.debug(f'{data}\nBatch Size: {batch_size}, Batch Count: {batch_count}')
		for batch in batches:
			rows = [
				dict(zip(chart.value_fields, row), **query_fields)
				for row in (batch.itertuples() if type(data) == pandas.DataFrame else batch.items())
			]
			insert_statement = insert(chart.table).values(rows)
			update_statement = insert_statement.on_duplicate_key_update({ x.name: x for x in insert_statement.inserted })
			database.engine.execute(update_statement)

		logger.info(f'Successfully wrote {chart} into database.')
		return chart

	def get_max_timestamp(self, chart: Chart) -> pandas.Timestamp:
		logger = self.logger.getChild('get_max_timestamp')
		logger.info(f'Getting the maximum timestamp available for {chart}...')
		select_statement = select(func.max(chart.model.timestamp))\
			.where(*[ getattr(chart.model, key) == getattr(chart, key) for key in chart.query_fields ])

		logger.debug(str(select_statement.compile()))
		result = database.engine.execute(select_statement).fetchone()[0]
		logger.info(f'Result: {result}')
		return result

	def get_min_timestamp(self, chart: Chart) -> pandas.Timestamp:
		logger = self.logger.getChild('get_min_timestamp')
		logger.info(f'Getting the minimum timestamp available for {chart}...')
		select_statement = select(func.min(chart.model.timestamp))\
			.where(*[ getattr(chart.model, key) == getattr(chart, key) for key in chart.query_fields ])
		logger.debug(str(select_statement.compile()))
		result = database.engine.execute(select_statement).fetchone()[0]
		logger.info(f'Result: {result}')
		return result

	def backtest(
		self,
		strategy: Strategy = None,
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
			# HACK: bypass chart.load and only read the timestamps
			query = select(trigger.model.timestamp)\
				.where(*[ getattr(trigger.model, key) == getattr(trigger, key) for key in trigger.query_fields ])\
				.where(trigger.model.timestamp.between(self.from_timestamp, self.to_timestamp))
			self.timesteps = pandas.DatetimeIndex([ step[0] for step in database.engine.execute(query).fetchall() ])
		elif isinstance(trigger, Interval):
			self.timesteps = pandas.date_range(self.from_timestamp, self.to_timestamp, freq=trigger.to_pandas_frequency, name='timesteps')
		else:
			raise Exception('Each strategy needs to define at least one trigger.')

		self.latency = latency
		self.scheduler = Scheduler()

		self.leverage = float(leverage)
		self.initial_cash = float(initial_cash)
		self.equity_curve = pandas.Series(index=self.timesteps, dtype='float', name='equity')

		self.positions: list[Position] = []
		self.orders: list[Order] = []

		if isclass(strategy):
			strategy = strategy(broker=self)

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
			try:
				if not strategy.is_aborted:
					strategy.handler()
			except Exception as exception:
				self.logger.error(f'Strategy {strategy} encountered an exception. Safely continuing...\n{exception}')
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
			self.logger.warn(f'Order is already placed: {order}')
			return

		order.id = random.randint(0, 1000000000)
		order.status = 'open'
		order.open_timestamp = order.broker.now
		self.orders.append(order)
		return order

	def fill_order(self, order: Order):
		if order.status != 'open':
			self.logger.warn(f"Cannot fill an order with status '{order.status}': {order}")
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
			self.logger.warning(f'Cannot cancel an order that has been filled: {order}')
			return

		order.status = 'cancelled'
		order.close_timestamp = self.now

	def close_position(self, position: Position, price=None):
		if position.status == 'closed':
			self.logger.warning(f'Cannot close a position that is already closed: {position}')
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
