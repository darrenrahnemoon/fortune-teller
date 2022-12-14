from keras.utils import Sequence

from core.chart.group import ChartGroup
from core.utils.mongo import get_mongo_client

class NextPeriodHighLowSequence(Sequence):
	def __init__(self, batch_size: int) -> None:
		self.batch_size = batch_size

	@classmethod
	def get_collection_for_chart_group(self, chart_group: ChartGroup):
		# HACK: generate the unique identifier of chart group here. Ideally get the individual datastructures to implement __hash__
		return str(hash((
			tuple(
				(
					tuple(getattr(chart, field) for field in chart.query_fields),
					tuple(chart.select),
					tuple(
						tuple(getattr(indicator, field) for field in indicator.value_fields)
						for indicator in chart.indicators
					)
				) for chart in self.chart_group.charts
			)
		)))