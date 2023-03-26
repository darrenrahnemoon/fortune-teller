from dataclasses import dataclass
from keras import Model
from keras.optimizers import Adam
from keras_tuner import HyperParameters

from apps.next_period_high_low.trainer.base import NextPeriodHighLowTrainerService
@dataclass
class NextPeriodHighLowTimeTrainerService(NextPeriodHighLowTrainerService):
	def compile(
		self,
		model: Model,
		hyperparameters: HyperParameters
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
			loss = [ 'mae' ],
		)
		return model
