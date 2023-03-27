import numpy
from keras import Model
from dataclasses import dataclass

from apps.next_period_high_low.preprocessor import NextPeriodHighLowPreprocessorService
from apps.next_period_high_low.config import NextPeriodHighLowStrategyConfig
from core.tensorflow.predictor.service import PredictorService
from core.utils.time import TimestampLike, normalize_timestamp

@dataclass
class NextPeriodHighLowPredictorService(PredictorService):
	strategy_config: NextPeriodHighLowStrategyConfig = None
	preprocessor_service: NextPeriodHighLowPreprocessorService = None

	def predict(self, model: Model, timestamp: TimestampLike):
		timestamp = normalize_timestamp(timestamp)
		input_chart_group = self.strategy_config.input_chart_group
		input_chart_group.read(to_timestamp = timestamp, refresh_indicators = False)
		for chart in input_chart_group.charts:
			chart.refresh_indicators()

		model_input = self.preprocessor_service.to_model_input(input_chart_group)
		model_input = numpy.array([ model_input ] * self.dataset_config.batch_size)
		with self.device_service.selected_device:
			model_output = model.predict(model_input)
			return self.preprocessor_service.from_model_output(model_output[0])
