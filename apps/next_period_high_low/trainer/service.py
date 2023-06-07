import tensorflow
import tensorflow._api.v2.math as math
from tensorflow import Tensor
from dataclasses import dataclass

from keras import Model
from keras.optimizers import Adam
from keras_tuner import HyperParameters
from keras.losses import mean_squared_error, binary_crossentropy
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
				learning_rate = self.config.learning_rate or hyperparameters.Float(
					name = 'learning_rate',
					min_value = 10 ** -4,
					max_value = 10 ** -3,
					step = 10 ** -4
				)
			),
			metrics = [ self.high_low_loss, self.direction_loss, self.direction_accuracy ],
			loss = self.loss,
		)

	def loss(self, y_true: Tensor, y_pred: Tensor):
		return self.high_low_loss(y_true, y_pred) + self.direction_loss(y_true, y_pred)

	def high_low_loss(self, y_true: Tensor, y_pred: Tensor):
		high_low_true = y_true[:, :, :2]
		high_low_pred = y_pred[:, :, :2]

		loss = mean_squared_error(high_low_true, high_low_pred)
		loss = tensorflow.reduce_sum(loss, axis = 1)
		loss = tensorflow.squeeze(loss)
		loss = loss * self.config.numerical_loss_scale

		return loss

	def direction_loss(self, y_true: Tensor, y_pred: Tensor):
		direction_true = y_true[:, :, 2]
		direction_pred = y_pred[:, :, 2]

		loss = binary_crossentropy(direction_true, direction_pred)
		loss = loss * self.config.direction_loss_scale
		return loss

	def direction_accuracy(self, y_true: Tensor, y_pred: Tensor):
		threshold = tensorflow.convert_to_tensor([ 0.5 ] * len(self.strategy_config.action.symbols))

		direction_true = y_true[:, :, 2]
		direction_true = math.greater(direction_true, threshold)

		direction_pred = y_pred[:, :, 2]
		direction_pred = math.greater(direction_pred, threshold)

		accuracy = tensorflow.cast(tensorflow.equal(direction_true, direction_pred), backend.floatx())
		accuracy = tensorflow.reduce_mean(accuracy)

		return accuracy