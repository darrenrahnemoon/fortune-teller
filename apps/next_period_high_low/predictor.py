import numpy
import pandas
from keras import Model
from dataclasses import dataclass

from apps.next_period_high_low.preprocessor import NextPeriodHighLowPreprocessorService
from apps.next_period_high_low.config import NextPeriodHighLowStrategyConfig
from core.tensorflow.predictor.service import PredictorService

@dataclass
class NextPeriodHighLowPredictorService(PredictorService):
	strategy_config: NextPeriodHighLowStrategyConfig = None
	preprocessor_service: NextPeriodHighLowPreprocessorService = None

	def predict(self, model: Model, timestamp: pandas.Timestamp):
		input_chart_group = self.strategy_config.input_chart_group
		input_chart_group.read(
			count = self.strategy_config.backward_window_bars,
			to_timestamp = timestamp,
			refresh_indicators = False
		)
		for chart in input_chart_group.charts:
			chart.refresh_indicators()

		model_input = self.preprocessor_service.to_model_input(input_chart_group)
		model_input = numpy.array([ model_input ] * self.dataset_config.batch_size)
		with self.device_service.selected_device:
			model_output = model.predict(model_input)
			return self.preprocessor_service.from_model_output(
				model_output[0],
				timestamp = timestamp,
			)

	def evaluate(
		self,
		model: Model,
		timestamp: pandas.Timestamp
	):
		predictions = self.predict(model, timestamp)
		chart_group = self.strategy_config.output_chart_group
		chart_group.read(
			from_timestamp = timestamp + self.strategy_config.interval.to_pandas_timedelta(),
			to_timestamp = timestamp + self.strategy_config.forward_window_length.to_pandas_timedelta(),
			count = None,
		)

		for prediction, chart in zip(predictions, chart_group.charts):
			if prediction.action == None:
				continue

			high = chart.data['high']
			low = chart.data['low']

			# SHOULD DO: get the actual spread at a point in time not just pip size * 2
			spread = self.strategy_config.metatrader_broker.repository.get_pip_size(chart.symbol) * 2

			if prediction.action == 'buy':
				tp_triggers = high[high >= prediction.tp + spread]
				prediction.tp_timestamp = tp_triggers.index[0] if len(tp_triggers) else None
				sl_triggers = low[low <= prediction.sl]
				prediction.sl_timestamp = sl_triggers.index[0] if len(sl_triggers) else None
			elif prediction.action == 'sell':
				tp_triggers = low[low >= prediction.tp - spread]
				prediction.tp_timestamp = tp_triggers.index[0] if len(tp_triggers) else None
				sl_triggers = high[high <= prediction.sl]
				prediction.sl_timestamp = sl_triggers.index[0] if len(sl_triggers) else None

		return predictions