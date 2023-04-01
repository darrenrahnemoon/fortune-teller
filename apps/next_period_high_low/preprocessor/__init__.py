import numpy
from dataclasses import dataclass
from core.chart import ChartGroup
from core.utils.logging import Logger

from apps.next_period_high_low.config import NextPeriodHighLowStrategyConfig
from core.tensorflow.preprocessor.service import PreprocessorService

logger = Logger(__name__)

@dataclass
class NextPeriodHighLowPreprocessorService(PreprocessorService):
	strategy_config: NextPeriodHighLowStrategyConfig = None
	scale = 1

	def to_model_input(self, input_chart_group: ChartGroup):
		input_chart_group.dataframe = input_chart_group.dataframe.tail(self.strategy_config.backward_window_bars)
		for chart in input_chart_group.charts:
			chart.data = chart.data.pct_change() * self.scale
		input_chart_group.dataframe = input_chart_group.dataframe.fillna(0)
		return input_chart_group.dataframe.to_numpy()

	def to_model_output(self, output_chart_group: ChartGroup):
		outputs = []
		output_chart_group.dataframe = output_chart_group.dataframe.fillna(method = 'ffill')

		nan_columns = output_chart_group.dataframe.columns[output_chart_group.dataframe.isna().any().tolist()]
		if len(nan_columns):
			logger.debug(f'Full NaN columns at {output_chart_group.dataframe.index[0]}:\n{nan_columns}')
			return
		output_chart_group.dataframe = output_chart_group.dataframe.reset_index(drop = True)
		for chart in output_chart_group.charts:
			high = chart.data['high']
			max_high_index = high.idxmax()
			max_high_change = high.max() / high.iloc[0] - 1

			low = chart.data['low']
			min_low_index = low.idxmin()
			min_low_change = low.min() / low.iloc[0] - 1

			outputs.append([
				max_high_change * self.scale,
				min_low_change * self.scale,
				(min_low_change if min_low_index < max_high_index else max_high_change) * self.scale
			])
		return numpy.array(outputs)

	def from_model_output(self, outputs: numpy.ndarray) -> list[dict]:
		return [
			{
				'symbol': chart.symbol,
				'max_high_change': output[0] / self.scale,
				'min_low_change': output[1] / self.scale,
				'tp_change' : output[2] / self.scale,
			}
			for chart, output in zip(self.strategy_config.output_chart_group.charts, outputs)
		]
