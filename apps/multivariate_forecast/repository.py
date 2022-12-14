from os import name
import pandas
from dataclasses import dataclass

from core.broker import SimulationBroker
from core.chart import ChartGroup, CandleStickChart

from core.utils.mongo import MongoRepository

@dataclass
class NextPeriodHighLowRepository(MongoRepository):
	def has_dataset(self, chart_group: ChartGroup) -> bool:
		return self.get_collection_for_chart_group(chart_group).count_documents({}) > 0

	def get_collection_for_chart_group(self, chart_group: ChartGroup):
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