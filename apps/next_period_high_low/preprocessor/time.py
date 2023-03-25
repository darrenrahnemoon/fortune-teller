import numpy
from dataclasses import dataclass

from core.utils.logging import Logger
from apps.next_period_high_low.preprocessor.base import NextPeriodHighLowPreprocessorService
from core.chart import ChartGroup

logger = Logger(__name__)

@dataclass
class NextPeriodHighLowTimePreprocessorService(NextPeriodHighLowPreprocessorService):
	def to_model_output(self, output_chart_group: ChartGroup):
		outputs = []

		nan_columns = output_chart_group.dataframe.columns[output_chart_group.dataframe.isna().any().tolist()]
		if len(nan_columns):
			logger.debug(f'Full NaN columns at {output_chart_group.dataframe.index[0]}:\n{nan_columns}')
			return

		output_chart_group.dataframe = output_chart_group.dataframe.reset_index(drop = True)

		for chart in output_chart_group.charts:
			max_high_index = chart.data['high'].idxmax()
			min_low_index = chart.data['low'].idxmin()
			outputs.append([
				max_high_index / self.strategy_config.forward_window_bars,
				min_low_index / self.strategy_config.forward_window_bars,
			])
		return numpy.array(outputs)

	def from_model_output(self, outputs: numpy.ndarray) -> list[dict]:
		return [
			{
				'symbol': chart.symbol,
				'max_high_index': output[0],
				'min_low_index': output[1]
			}
			for chart, output in zip(self.strategy_config.output_chart_group.charts, outputs)
		]
