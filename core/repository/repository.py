import pandas
from abc import abstractmethod
from typing import TYPE_CHECKING, ClassVar
from dataclasses import dataclass
if TYPE_CHECKING:
	from core.chart import Chart

from core.utils.time import now
from core.utils.cls import product_dict
from core.utils.collection import is_any_of

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
	def write_chart(
		self,
		chart: 'Chart' = None,
		**overrides
	) -> None:
		pass
