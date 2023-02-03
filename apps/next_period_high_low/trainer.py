import numpy
from keras import Model
from dataclasses import dataclass

from .preprocessor import NextPeriodHighLowPreprocessorService
from .config import NextPeriodHighLowStrategyConfig
from core.tensorflow.trainer.service import TrainerService
from core.utils.time import TimestampLike, normalize_timestamp

@dataclass
class NextPeriodHighLowTrainerService(TrainerService):
	strategy_config: NextPeriodHighLowStrategyConfig = None
	preprocessor_service: NextPeriodHighLowPreprocessorService = None

	def predict(self, model: Model, timestamp: TimestampLike):
		timestamp = normalize_timestamp(timestamp)
		input_chart_group = self.strategy_config.input_chart_group
		input_chart_group.read(to_timestamp = timestamp, refresh_indicators = False)
		for chart in input_chart_group.charts:
			chart.refresh_indicators()

		model_input = self.preprocessor_service.to_model_input(input_chart_group)
		model_input = numpy.array([ model_input ] * self.dataset_service.config.batch_size)
		with self.device.selected_device:
			model_output = model.predict(model_input)
			return self.preprocessor_service.from_model_output(model_output[0])

