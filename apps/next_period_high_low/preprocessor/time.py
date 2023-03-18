import numpy
from dataclasses import dataclass

from apps.next_period_high_low.preprocessor.base import NextPeriodHighLowPreprocessorService
from core.chart import ChartGroup

@dataclass
class NextPeriodHighLowTimePreprocessorService(NextPeriodHighLowPreprocessorService):
	def to_model_output(self, output_chart_group: ChartGroup):
		outputs = []
		output_chart_group.dataframe = output_chart_group.dataframe.fillna(method = 'ffill')
		output_chart_group.dataframe = output_chart_group.dataframe.fillna(0)

		for chart in output_chart_group.charts:
			current_timestamp = chart.data.index[0]
			max_high_change_time_offset = chart.data['high'].idxmax() - current_timestamp
			min_low_change_time_offset = chart.data['low'].idxmin() - current_timestamp

			max_high_change_time_offset = max_high_change_time_offset / self.strategy_config.interval.to_pandas_timedelta()
			min_low_change_time_offset = min_low_change_time_offset / self.strategy_config.interval.to_pandas_timedelta()

			outputs.append([
				max_high_change_time_offset,
				min_low_change_time_offset
			])
		return numpy.array(outputs)

	def from_model_output(self, outputs: numpy.ndarray) -> list[dict]:
		return [
			{
				'symbol': chart.symbol,
				'max_high_change_time_offset': output[0],
				'min_low_change_time_offset': output[1]
			}
			for chart, output in zip(self.strategy_config.output_chart_group.charts, outputs)
		]
