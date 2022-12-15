import pandas
from dataclasses import dataclass
from pymongo.collection import Collection

from core.chart import ChartGroup
from core.utils.mongo import MongoRepository

@dataclass
class NextPeriodHighLowRepository(MongoRepository):
	def get_collection_for_chart_group(self, chart_group: ChartGroup) -> Collection:
		# HACK: generate the unique identifier of chart group here. Ideally get the individual datastructures to implement __hash__
		return self.training_datasets[
			str(
				hash(
					tuple(
						(
							chart.name,
							tuple(chart.select),
							tuple(
								tuple(field for field in indicator.value_fields)
								for indicator in chart.indicators
							)
						) for chart in chart_group.charts
					)
				)
			)
		]

	@property
	def training_datasets(self):
		return self.client['training_datasets']