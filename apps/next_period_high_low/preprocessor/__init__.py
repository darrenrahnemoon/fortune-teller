import numpy
import pandas
from dataclasses import dataclass
from core.chart import ChartGroup
from core.utils.logging import Logger

from apps.next_period_high_low.config import NextPeriodHighLowStrategyConfig
from apps.next_period_high_low.preprocessor.prediction import NextPeriodHighLowPrediction, NextPeriodHighLowModelOutput

from core.tensorflow.preprocessor.service import PreprocessorService

logger = Logger(__name__)

@dataclass
class NextPeriodHighLowPreprocessorService(PreprocessorService):
	strategy_config: NextPeriodHighLowStrategyConfig = None
	scale = 1

	def to_model_input(self, input_chart_group: ChartGroup):
		input_chart_group.dataframe = input_chart_group.dataframe.tail(self.strategy_config.observation.bars)
		for chart in input_chart_group.charts:
			data = chart.data.copy()

			# Forward fill missing spread data
			if 'spread_pips' in data.columns:
				data['spread_pips'] = data['spread_pips'].replace(to_replace = 0, method = 'ffill')
				data['spread_pips'] = data['spread_pips'] + 2 # to prevent log returning 0 when spread is `1`
				data['spread_pips'] = numpy.log(data['spread_pips'])

			# Log normalize the volume
			if 'volume_tick' in data.columns:
				if not data['volume_tick'].isna().all():
					data['volume_tick'] = data['volume_tick'] + 2 # to prevent log returning 0 when volume is `1`
					data['volume_tick'] = numpy.log(data['volume_tick'])

			# Convert to `change`
			data = data.pct_change()

			# Final Scaling
			data = data * self.scale

			chart.data = data
		input_chart_group.dataframe = input_chart_group.dataframe.fillna(0)
		return { 'foo': input_chart_group.dataframe.to_numpy() }

	def to_model_output(self, output_chart_group: ChartGroup):
		outputs = []
		output_chart_group.dataframe = output_chart_group.dataframe.head(self.strategy_config.action.bars)
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

	def from_model_output(
		self,
		outputs: numpy.ndarray,
		timestamp: pandas.Timestamp = None
	):
		output_chart_group = self.strategy_config.action.build_chart_group()
		return [
			NextPeriodHighLowPrediction(
				model_output = NextPeriodHighLowModelOutput(
					max_high_change = output[0] / self.scale,
					min_low_change = output[1] / self.scale,
					tp_change = output[2] / self.scale,
				),
				symbol = chart.symbol,
				broker = self.strategy_config.action.broker,
				strategy_config = self.strategy_config,
				timestamp = timestamp,
			)
			for chart, output in zip(output_chart_group.charts, outputs)
		]
