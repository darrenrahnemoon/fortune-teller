import numpy
from keras import Model
from dataclasses import dataclass

from .preprocessor import NextPeriodHighLowPreprocessor
from .config import NextPeriodHighLowStrategyConfig
from core.tensorflow.trainer.service import TrainerService
from core.utils.time import TimestampLike, normalize_timestamp

@dataclass
class NextPeriodHighLowTrainerService(TrainerService):
	strategy_config: NextPeriodHighLowStrategyConfig = None
	preprocessor: NextPeriodHighLowPreprocessor = None

	def predict(self, model: Model, timestamp: TimestampLike):
		timestamp = normalize_timestamp(timestamp)
		input_chart_group = self.strategy_config.input_chart_group
		input_chart_group.read(to_timestamp = timestamp)

		self.preprocessor.process_input(
			input_chart_group,
			truncate_from = 'tail',
			truncate_len = self.strategy_config.backward_window_length
		)
		model_input = self.preprocessor.to_model_input(input_chart_group)
		model_input = numpy.array([ model_input ] * self.dataset.config.batch_size)
		with self.device.selected:
			model_output = model.predict(model_input)
			return self.preprocessor.from_model_output(model_output[0])

