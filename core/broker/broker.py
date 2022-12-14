import abc
import typing
from dataclasses import dataclass

from core.order import Order, OrderStatus, OrderType
from core.position import Position, PositionStatus, PositionType
if typing.TYPE_CHECKING:
	from core.chart import Chart, Symbol

from core.utils.time import TimestampLike, now
from core.utils.cls import product_dict

ChartCombinations = dict[
	type['Chart'], dict[str, list]
]

@dataclass
class Broker:
	timezone = 'UTC'

	@property
	def now(self):
		return now(self.timezone)

	@abc.abstractmethod
	def get_available_chart_combinations(self) -> ChartCombinations:
		pass

	@classmethod
	def get_available_charts(self, filter = {}):
		charts = []
		for chart, combination_groups in self.get_available_chart_combinations().items():
			if 'chart' in filter and not issubclass(chart, filter['chart']):
				continue
			for combination_group in combination_groups:
				for combination in product_dict(combination_group):
					if filter.items() <= combination.items():
						charts.append(chart(**combination))
		return charts

	def ensure_timestamp(self, chart: 'Chart'):
		if chart.count:
			if chart.to_timestamp:
				raise Exception('Cannot read x number of datapoints before a timestamp.')
			if chart.from_timestamp:
				return
		if not chart.to_timestamp:
			chart.to_timestamp = self.now

	@abc.abstractmethod
	def read_chart(self, chart: 'Chart'):
		pass

	@abc.abstractmethod
	def write_chart(self, chart: 'Chart'):
		pass

	@abc.abstractmethod
	def place_order(self, order: Order) -> Order:
		pass

	@abc.abstractmethod
	def cancel_order(self, order: Order) -> Order:
		pass

	@abc.abstractmethod
	def close_position(self, position: Position):
		pass

	@abc.abstractmethod
	def get_last_price(self, symbol: 'Symbol') -> float:
		pass

	@abc.abstractmethod
	def get_orders(
		self,
		symbol: 'Symbol' = None,
		type: OrderType = None,
		from_timestamp: TimestampLike = None,
		to_timestamp: TimestampLike = None,
		status: OrderStatus = None,
	) -> list[Order]:
		pass

	@abc.abstractmethod
	def get_positions(
		self,
		symbol: 'Symbol' = None,
		type: PositionType = None,
		from_timestamp: TimestampLike = None,
		to_timestamp: TimestampLike = None,
		status: PositionStatus = None,
	) -> list[Position]:
		pass

	@abc.abstractproperty
	def balance(self) -> float:
		pass

	@abc.abstractproperty
	def equity(self) -> float:
		pass

	@abc.abstractproperty
	def leverage(self) -> float:
		pass

	@property
	def margin(self) -> float:
		return 1 / self.leverage
