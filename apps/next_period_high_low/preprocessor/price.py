import numpy
from dataclasses import dataclass

from apps.next_period_high_low.preprocessor.base import NextPeriodHighLowPreprocessorService
from core.chart import ChartGroup

@dataclass
class NextPeriodHighLowPricePreprocessorService(NextPeriodHighLowPreprocessorService):
	def to_model_output(self, output_chart_group: ChartGroup):
		outputs = []
		output_chart_group.dataframe = output_chart_group.dataframe.fillna(method = 'ffill')
		output_chart_group.dataframe = output_chart_group.dataframe.fillna(0)

		for chart in output_chart_group.charts:
			current_high = chart.data['high'].iloc[0]
			if current_high == 0:
				max_high_percentage_change = 0
			else:
				max_high_percentage_change = chart.data['high'].max() / current_high - 1

			current_low = chart.data['low'].iloc[0]
			if current_low == 0:
				min_low_percentage_change = 0
			else:
				min_low_percentage_change = chart.data['low'].min() / current_low - 1

			outputs.append([
				max_high_percentage_change,
				min_low_percentage_change
			])
		return numpy.array(outputs)

	def from_model_output(self, outputs: numpy.ndarray) -> list[dict]:
		return [
			{
				'symbol': chart.symbol,
				'max_high_percentage_change': output[0],
				'min_low_percentage_change': output[1]
			}
			for chart, output in zip(self.strategy_config.output_chart_group.charts, outputs)
		]
