import numpy
import pandas
from keras import Model
from dataclasses import dataclass

from examples.ave_maria.tensorflow.preprocessor.service import AveMariaPreprocessorService
from examples.ave_maria.trading.config import AveMariaTradingConfig
from core.tensorflow.predictor.service import PredictorService

@dataclass
class AveMariaPredictorService(PredictorService):
	trading_config: AveMariaTradingConfig = None
	preprocessor_service: AveMariaPreprocessorService = None

	def predict(self, model: Model, timestamp: pandas.Timestamp):
		input_chart_groups = self.trading_config.observation.build_chart_group()
		for input_chart_group in input_chart_groups.values():
			input_chart_group.read(
				count = self.trading_config.observation.bars,
				to_timestamp = timestamp,
				refresh_indicators = False
			)
			for chart in input_chart_group.charts:
				chart.refresh_indicators()

		model_input = self.preprocessor_service.to_model_input(input_chart_groups)
		model_input = { 
			key: numpy.expand_dims(value, axis = 0)
			for key, value in model_input.items()
		}
		with self.device_service.selected_device:
			model_output = model.predict(model_input)
			return self.preprocessor_service.to_prediction(
				model_output,
				timestamp = timestamp,
			)

	def evaluate(
		self,
		model: Model,
		timestamp: pandas.Timestamp
	):
		predictions = self.predict(model, timestamp)
		output_chart_group = self.trading_config.action.build_chart_group()
		output_chart_group.read(
			from_timestamp = timestamp + self.trading_config.action.interval.to_pandas_timedelta(),
			to_timestamp = timestamp + self.trading_config.action.period.to_pandas_timedelta(),
			count = None,
		)

		for prediction, chart in zip(predictions, output_chart_group.charts):
			if prediction.action == None:
				continue

			high = chart.data['high']
			low = chart.data['low']

			# SHOULD DO: get the actual spread at a point in time not just pip size * 2
			spread = self.trading_config.action.broker.repository.get_pip_size(chart.symbol) * 2

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