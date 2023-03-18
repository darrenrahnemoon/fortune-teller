import numpy
from dataclasses import dataclass

from apps.next_period_high_low.preprocessor.base import NextPeriodHighLowPreprocessorService
from core.tensorflow.dataset.sequence.skippable import SkipItemException
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
			raise SkipItemException()

		for chart in output_chart_group.charts:
			current_high = chart.data['high'].iloc[0]
			if current_high == 0:
				high = 0
			else:
				high = chart.data['high'].max() / current_high - 1

			current_low = chart.data['low'].iloc[0]
			if current_low == 0:
				low = 0
			else:
				low = chart.data['low'].min() / current_low - 1

			current_close = chart.data['close'].iloc[0]
			if current_close == 0:
				close = 0
			else:
				close = chart.data['close'].iloc[-1] / current_close - 1

			outputs.append([
				high,
				low,
				close
			])
		return numpy.array(outputs)

	def from_model_output(self, outputs: numpy.ndarray) -> list[dict]:
		return [
			{
				'symbol': chart.symbol,
				'high_change': output[0],
				'low_change': output[1],
				'close_change': output[2],
			}
			for chart, output in zip(self.strategy_config.output_chart_group.charts, outputs)
		]
