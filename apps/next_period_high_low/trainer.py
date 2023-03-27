from dataclasses import dataclass
from keras import Model
from keras.optimizers import Adam
from keras_tuner import HyperParameters

from apps.next_period_high_low.config import NextPeriodHighLowStrategyConfig
from core.tensorflow.trainer.service import TrainerService

@dataclass
class NextPeriodHighLowTrainerService(TrainerService):
	strategy_config: NextPeriodHighLowStrategyConfig = None

	def compile(
		self,
		model: Model,
		hyperparameters: HyperParameters = None,
	):
		model.compile(
			optimizer = Adam(
				learning_rate = self.config.learning_rate or hyperparameters.Float(
					name = 'learning_rate',
					min_value = 10 ** -4,
					max_value = 10 ** -3,
					step = 10 ** -4
				)
			),
			loss = 'mae',
		)