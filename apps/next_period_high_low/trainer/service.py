import tensorflow
import tensorflow._api.v2.math as math
from tensorflow import Tensor
from dataclasses import dataclass

from keras import Model
from keras.optimizers import Adam
from keras_tuner import HyperParameters
from keras.losses import mean_squared_error, categorical_crossentropy
import keras.backend as backend

from apps.next_period_high_low.config import NextPeriodHighLowStrategyConfig
from apps.next_period_high_low.trainer.config import NextPeriodHighLowTrainerConfig
from core.tensorflow.trainer.service import TrainerService

@dataclass
class NextPeriodHighLowTrainerService(TrainerService):
	config: NextPeriodHighLowTrainerConfig = None
	strategy_config: NextPeriodHighLowStrategyConfig = None

	def compile(
		self,
		model: Model,
		hyperparameters: HyperParameters = None,
	):
		model.compile(
			optimizer = Adam(
				learning_rate = self.config.learning_rate or 0.0001
			),
			metrics = {
				'direction' : [ self.direction_accuracy ],
			},
			loss = {
				'direction' : self.direction_loss,
				'high_low' : self.high_low_loss,
			},
			loss_weights = {
				'direction' : self.config.direction_loss_weight,
				'high_low' : self.config.high_low_loss_weight,
			}
		)

	def high_low_loss(self, y_true: Tensor, y_pred: Tensor):
		high_low_true = y_true[:, :, :]
		high_low_pred = y_pred[:, :, :]

		loss = mean_squared_error(high_low_true, high_low_pred)
		loss = tensorflow.reduce_mean(loss, axis = 1)
		return loss

	def direction_loss(self, y_true: Tensor, y_pred: Tensor):
		direction_true = y_true[:, :, :]
		direction_pred = y_pred[:, :, :]

		loss = categorical_crossentropy(direction_true, direction_pred)
		loss = tensorflow.reduce_mean(loss, axis = 1)
		return loss

	def direction_accuracy(self, y_true: Tensor, y_pred: Tensor):
		direction_true = y_true[:, :, :]
		direction_true = math.greater(direction_true, 0.5)

		direction_pred = y_pred[:, :, :]
		direction_pred = math.greater(direction_pred, 0.5)

		accuracy = tensorflow.cast(tensorflow.equal(direction_true, direction_pred), backend.floatx())
		accuracy = tensorflow.reduce_mean(accuracy)

		return accuracy