import pandas
from abc import abstractmethod
from typing import TYPE_CHECKING, ClassVar
from dataclasses import dataclass
if TYPE_CHECKING:
	from core.chart import Chart

from core.utils.time import now
from core.utils.cls import product_dict

ChartCombinations = dict[
	type['Chart'], dict[str, list]
]

@dataclass
class Repository:
	timezone: ClassVar[str] = 'UTC'

	@abstractmethod
	def get_available_chart_combinations(self) -> ChartCombinations:
		pass

	def get_available_charts(self, filter = {}, **kwargs):
		charts = []
		for chart, combination_groups in self.get_available_chart_combinations().items():
			if 'chart' in filter and not issubclass(chart, filter['chart']):
				continue
			for combination_group in combination_groups:
				for combination in product_dict(combination_group):
					if filter.items() <= combination.items():
						charts.append(chart(**combination))
		return charts

	@abstractmethod
	def read_chart(
		self,
		chart: 'Chart' = None,
		**overrides
	) -> pandas.DataFrame:
		pass

	@abstractmethod
	def write_chart(
		self,
		chart: 'Chart' = None,
		**overrides
	) -> None:
		pass
