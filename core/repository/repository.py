import pandas
from abc import abstractmethod
from typing import TYPE_CHECKING, ClassVar
from dataclasses import dataclass
if TYPE_CHECKING:
	from core.chart import Chart, Symbol

from core.utils.time import now
from core.utils.cls import product_dict
from core.utils.collection import is_any_of

ChartCombinations = dict[
	type['Chart'], dict[str, list]
]

@dataclass
class Repository:
	timezone: ClassVar[str] = 'UTC'

	@property
	def now(self):
		return now(self.timezone)

	@abstractmethod
	def get_available_chart_combinations(self) -> ChartCombinations:
		pass

	def get_available_symbols(self):
		symbols = set()
		for _, combinations in self.get_available_chart_combinations().items():
			for combination in combinations:
				for symbol in combination['symbol']:
					symbols.add(symbol)
		return list(symbol)

	def get_available_charts(self, filter = {}, **kwargs):
		for chart, combination_groups in self.get_available_chart_combinations().items():
			if 'chart' in filter and not is_any_of(filter['chart'], lambda filter_chart: issubclass(chart, filter_chart)):
				continue
			for combination_group in combination_groups:
				for combination in product_dict(combination_group):
					should_skip = False
					for key, value in combination.items():
						if key in filter and not value in filter[key]:
							should_skip = True
							break
					if should_skip:
						continue
					yield chart(**combination)

	@abstractmethod
	def read_chart(
		self,
		chart: 'Chart' = None,
		**overrides
	) -> pandas.DataFrame:
		pass

	@abstractmethod
	def get_last_price(
		self,
		symbol: 'Symbol',
		timestamp: pandas.Timestamp = None
	) -> float:
		pass

	@abstractmethod
	def write_chart(
		self,
		chart: 'Chart' = None,
		**overrides
	) -> None:
		pass

	def convert_currency(amount, from_currency: str, to_currency: str):
		if from_currency == to_currency:
			return amount

	@abstractmethod
	def get_spread(self, symbol: 'Symbol'):
		pass

	@abstractmethod
	def get_pip_size(self, symbol: 'Symbol'):
		return self.get_point_size(symbol) * 10

	@abstractmethod
	def get_point_size(self, symbol: 'Symbol'):
		pass

	@abstractmethod
	def get_base_currency(self, symbol: 'Symbol'):
		pass

	@abstractmethod
	def get_quote_currency(self, symbol: 'Symbol'):
		pass
