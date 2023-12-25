import numpy
import pandas
from dataclasses import dataclass

from core.trading.chart import ChartGroup
from core.trading.interval import Interval
from core.utils.logging import Logger

from apps.ave_maria.config import AveMariaTradingConfig
from apps.ave_maria.tensorflow.preprocessor.prediction import AveMariaPrediction, AveMariaModelOutput

from core.tensorflow.preprocessor.service import PreprocessorService

logger = Logger(__name__)

@dataclass
class AveMariaPreprocessorService(PreprocessorService):
	trading_config: AveMariaTradingConfig = None

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
			chart_group.dataframe = chart_group.dataframe.tail(self.trading_config.observation.bars)
		inputs = {
			str(interval): chart_group.dataframe.to_numpy()
			for interval, chart_group in input_chart_groups.items()
		}
		return inputs

	def to_model_output(self, output_chart_group: ChartGroup):
		outputs = {
			'direction' : [],
			'high_low' : []
		}

		output_chart_group.dataframe = output_chart_group.dataframe.fillna(method = 'ffill')

		nan_columns = output_chart_group.dataframe.columns[output_chart_group.dataframe.isna().any().tolist()]
		if len(nan_columns):
			logger.debug(f'Full NaN columns at {output_chart_group.dataframe.index[0]}:\n{nan_columns}')
			return

		output_chart_group.dataframe = output_chart_group.dataframe.head(self.trading_config.action.bars)
		output_chart_group.dataframe = output_chart_group.dataframe.fillna(0)

		output_chart_group.dataframe = output_chart_group.dataframe.reset_index(drop = True)
		for chart in output_chart_group.charts:
			high_low = []
			direction = []
			for window_length in self.trading_config.action.window_lengths:
				min_low = chart.data['low'].iloc[0:window_length].min() / chart.data['low'].iloc[0] - 1
				min_low_index = chart.data['low'].iloc[0:window_length].idxmin()
				max_high = chart.data['high'].iloc[0:window_length].max() / chart.data['high'].iloc[0] - 1
				max_high_index = chart.data['high'].iloc[0:window_length].idxmax()
				high_low.append([
					max_high,
					min_low,
				])
				if min_low_index < max_high_index:
					direction.append(min_low)
				elif min_low_index > max_high_index:
					direction.append(max_high)
				else:
					direction.append(0)

			outputs['high_low'].append(high_low)
			outputs['direction'].append(direction)
		outputs = {
			key: numpy.array(value)
			for key, value in outputs.items()
		}
		return outputs

	def to_prediction(
		self,
		outputs: dict, # dict['direction' | 'high_low', (batch, chart, values)]
		timestamp: pandas.Timestamp = None
	):
		output_chart_group = self.trading_config.action.build_chart_group()
		return [
			AveMariaPrediction(
				model_output = AveMariaModelOutput(
					max_high_change = outputs['high_low'][0][index][0],
					min_low_change = outputs['high_low'][0][index][1],
					direction = numpy.greater(outputs['direction'][0][index], 0.5),
				),
				symbol = chart.symbol,
				broker = self.trading_config.action.broker,
				trading_config = self.trading_config,
				timestamp = timestamp,
			)
			for index, chart in enumerate(output_chart_group.charts)
		]
