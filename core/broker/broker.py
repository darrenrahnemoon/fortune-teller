import inspect
import pandas
import typing

from core.order import Order
from core.position import Position
from core.chart import Chart
from core.strategy import Strategy
from core.utils.time import now
from core.utils.cls import instance_to_repr

class Broker:
	timezone = 'UTC'
	intervals = {}

	def __init__(
		self,
		strategies: list[Strategy or type[Strategy]] = []
	) -> None:
		self.strategies: list[Strategy] = []
		for strategy in strategies:
			self.add_strategy(strategy)

	@classmethod
	def from_repr(cls, _repr: str):
		return next(broker for broker in cls.__subclasses__() if broker.__name__ in _repr)

	@property
	def name(self):
		return type(self).__name__

	def __str__(self) -> str:
		return self.name

	def __repr__(self) -> str:
		return instance_to_repr(self)

	def add_strategy(self, strategy: Strategy or type[Strategy]):
		if inspect.isclass(strategy):
			strategy = strategy()
		if not isinstance(strategy, Strategy):
			raise Exception('Invalid argument passed to strategy. Must be either a Strategy subclass or instance.')
		strategy.broker = self
		self.strategies.append(strategy)

	@property
	def now(self):
		return now(self.timezone)

	@property
	def available_data(self) -> dict[str, dict[Chart, dict[str, typing.Any]]]:
		raise NotImplemented()

	def ensure_timestamp(self, chart: Chart):
		if not chart.from_timestamp:
			raise Exception("'from_timestamp' is required.")
		if not chart.to_timestamp:
			chart.to_timestamp = self.now
		return chart

	def read_chart(self, chart: Chart) -> Chart:
		raise NotImplemented()

	def write_chart(self, chart: Chart) -> Chart:
		raise NotImplemented()

	def place_order(self, order: Order) -> Order:
		raise NotImplemented()

	def cancel_order(self, order: Order) -> Order:
		raise NotImplemented()

	def close_position(self, position: Position):
		raise NotImplemented()

	def get_last_price(self, symbol: str) -> float:
		raise NotImplemented()

	def get_orders(
		self,
		symbol: str = None,
		from_timestamp: pandas.Timestamp = None,
		to_timestamp: pandas.Timestamp = None,
		status: str = None, # 'open', 'filled', 'cancelled'
	) -> list[Order]:
		raise NotImplemented()

	def get_positions(
		self,
		symbol: str = None,
		from_timestamp: pandas.Timestamp = None,
		to_timestamp: pandas.Timestamp = None,
		status: str = None, # 'open', 'closed'
	) -> list[Position]:
		raise NotImplemented()

	@property
	def balance(self) -> float:
		raise NotImplemented()

	@property
	def equity(self) -> float:
		raise NotImplemented()

	@property
	def leverage(self) -> float:
		raise NotImplemented()

	@property
	def margin(self) -> float:
		return 1 / self.leverage
