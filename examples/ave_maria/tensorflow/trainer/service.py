import tensorflow
import tensorflow._api.v2.math as math
from tensorflow import Tensor
from dataclasses import dataclass

from keras import Model
from keras.optimizers import Adam
from keras_tuner import HyperParameters
from keras.losses import mean_squared_error, binary_crossentropy
import keras.backend as backend

from apps.ave_maria.config import AveMariaTradingConfig
from apps.ave_maria.tensorflow.trainer.config import AveMariaTrainerConfig
from core.tensorflow.trainer.service import TrainerService

@dataclass
class AveMariaTrainerService(TrainerService):
	config: AveMariaTrainerConfig = None
	trading_config: AveMariaTradingConfig = None

	def compile(
		self,
		model: Model,
		hyperparameters: HyperParameters = None,
	):
		model.compile(
			optimizer = Adam(
				learning_rate = self.config.learning_rate or 0.001,
			),
			# metrics = {
			# 	'direction' : [ self.direction_accuracy ],
			# },
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
		loss = mean_squared_error(y_true, y_pred)
		loss = tensorflow.reduce_mean(loss, axis=[1, 2])
		return loss

	def direction_loss(self, y_true: Tensor, y_pred: Tensor):
		# loss = binary_crossentropy(y_true, y_pred, from_logits=True)
		loss = mean_squared_error(y_true, y_pred)
		loss = tensorflow.reduce_mean(loss, axis=-1)
		return loss

	# def direction_accuracy(self, y_true: Tensor, y_pred: Tensor):
	# 	direction_true = math.greater(y_true, 0)
	# 	direction_pred = math.greater(y_pred, 0)

	# 	accuracy = tensorflow.cast(tensorflow.equal(direction_true, direction_pred), backend.floatx())
	# 	accuracy = tensorflow.reduce_mean(accuracy, axis = [1, 2])

	# 	return accuracy