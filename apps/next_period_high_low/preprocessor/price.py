import numpy
from dataclasses import dataclass

from apps.next_period_high_low.preprocessor.base import NextPeriodHighLowPreprocessorService
from core.utils.logging import Logger
from core.chart import ChartGroup

logger = Logger(__name__)

@dataclass
class NextPeriodHighLowPricePreprocessorService(NextPeriodHighLowPreprocessorService):
	def to_model_output(self, output_chart_group: ChartGroup):
		outputs = []
		output_chart_group.dataframe = output_chart_group.dataframe.fillna(method = 'ffill')

		nan_columns = output_chart_group.dataframe.columns[output_chart_group.dataframe.isna().any().tolist()]
		if len(nan_columns):
			logger.debug(f'Full NaN columns at {output_chart_group.dataframe.index[0]}:\n{nan_columns}')
			return

		for chart in output_chart_group.charts:
			high = chart.data['high']
			max_high_change = high.max() / high.iloc[0] - 1
			average_high_change = high.sum() / len(high) / high.iloc[0] - 1

			low = chart.data['low']
			min_low_change = low.min() / low.iloc[0] - 1
			average_low_change = low.sum() / len(low) / low.iloc[0] - 1

			outputs.append([
				max_high_change,
				average_high_change,
				min_low_change,
				average_low_change,
			])
		return numpy.array(outputs)

	def from_model_output(self, outputs: numpy.ndarray) -> list[dict]:
		return [
			{
				'symbol': chart.symbol,
				'max_high_change': output[0],
				'average_high_change': output[1],
				'min_low_change': output[2],
				'average_low_change': output[3],
			}
			for chart, output in zip(self.strategy_config.output_chart_group.charts, outputs)
		]
