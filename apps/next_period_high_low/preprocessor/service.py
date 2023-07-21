import numpy
import pandas
from dataclasses import dataclass
from core.chart import ChartGroup
from core.interval import Interval
from core.utils.logging import Logger

from apps.next_period_high_low.config import NextPeriodHighLowStrategyConfig
from apps.next_period_high_low.preprocessor.prediction import NextPeriodHighLowPrediction, NextPeriodHighLowModelOutput

from core.tensorflow.preprocessor.service import PreprocessorService

logger = Logger(__name__)

@dataclass
class NextPeriodHighLowPreprocessorService(PreprocessorService):
	strategy_config: NextPeriodHighLowStrategyConfig = None

	def to_model_input(self, input_chart_groups: dict[Interval, ChartGroup]):
		for interval, chart_group in input_chart_groups.items():
			nan_columns = chart_group.dataframe.columns[chart_group.dataframe.isna().all().tolist()]
			if len(nan_columns):
				logger.debug(f'Full NaN columns at {chart_group.dataframe.index[0]}:\n{nan_columns}\n\n{chart_group.dataframe}')
				return

			for chart in chart_group.charts:
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

				chart.data = data
			chart_group.dataframe = chart_group.dataframe.fillna(0)
			chart_group.dataframe = chart_group.dataframe.tail(self.strategy_config.observation.bars)
		return {
			str(interval): chart_group.dataframe.to_numpy()
			for interval, chart_group in input_chart_groups.items()
		}

	def to_model_output(self, output_chart_group: ChartGroup):
		outputs = {
			'direction' : [],
			'high_low' : []
		}
		high_low_outputs = []

		output_chart_group.dataframe = output_chart_group.dataframe.head(self.strategy_config.action.bars)
		output_chart_group.dataframe = output_chart_group.dataframe.fillna(method = 'ffill')

		nan_columns = output_chart_group.dataframe.columns[output_chart_group.dataframe.isna().any().tolist()]
		if len(nan_columns):
			logger.debug(f'Full NaN columns at {output_chart_group.dataframe.index[0]}:\n{nan_columns}')
			return

		output_chart_group.dataframe = output_chart_group.dataframe.reset_index(drop = True)
		for chart in output_chart_group.charts:
			top_datapoints_count = int(0.1 * len(chart.data))

			high = chart.data['high']
			high_index_sorted = high.argsort()
			high_sorted = numpy.sort(high)
			median_max_high_index = numpy.median(high_index_sorted[-1 * top_datapoints_count:])
			median_max_high_change = numpy.median(high_sorted[-1 * top_datapoints_count:]) / high.iloc[0] - 1

			low = chart.data['low']
			low_index_sorted = low.argsort()
			low_sorted = numpy.sort(low)
			median_min_low_index = numpy.median(low_index_sorted[:top_datapoints_count])
			median_min_low_change = numpy.median(low_sorted[:top_datapoints_count]) / low.iloc[0] - 1

			is_uncertain = numpy.isclose(median_max_high_index, median_min_low_index, atol = top_datapoints_count)
			if is_uncertain:
				is_long = 0
				is_short = 0
			else:
				is_long = int(median_max_high_index < median_min_low_index)
				is_short = int(not median_max_high_index)

			outputs['high_low'].append([
				median_max_high_change,
				median_min_low_change,
			])
			outputs['direction'].append([
				is_long,
				is_short
			])
		outputs = {
			key: numpy.array(value)
			for key, value in outputs.items()
		}
		return outputs

	def from_model_output(
		self,
		outputs: dict, # dict['direction' | 'high_low', (batch, chart, values)]
		timestamp: pandas.Timestamp = None
	):
		output_chart_group = self.strategy_config.action.build_chart_group()
		return [
			NextPeriodHighLowPrediction(
				model_output = NextPeriodHighLowModelOutput(
					max_high_change = outputs['high_low'][0][index][0],
					min_low_change = outputs['high_low'][0][index][1],
					direction = numpy.greater(outputs['direction'][0][index], 0.5),
				),
				symbol = chart.symbol,
				broker = self.strategy_config.action.broker,
				strategy_config = self.strategy_config,
				timestamp = timestamp,
			)
			for index, chart in enumerate(output_chart_group.charts)
		]
