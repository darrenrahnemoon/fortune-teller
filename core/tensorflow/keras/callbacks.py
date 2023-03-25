from keras.callbacks import Callback
from keras.utils.layer_utils import count_params
from core.utils.logging import Logger

logger = Logger(__name__)

class EarlyStoppingByModelSize(Callback):
	def __init__(
		self,
		min_size: int = None,
		max_size: int = None
	):
		self.min_size = min_size
		self.max_size = max_size

	def on_train_begin(self, logs: dict[str] = {}):
		trainable_count = count_params(self.model.trainable_weights)
		if self.max_size and trainable_count > self.max_size:
			self.model.stop_training = True
			logger.warn(f'Skipping model due to size {trainable_count} > {self.max_size}')
		if self.min_size and trainable_count < self.min_size:
			self.model.stop_training = True
			logger.warn(f'Skipping model due to size: {trainable_count} < {self.min_size}')

class AverageAccuracy(Callback):
	def on_epoch_end(self, epoch, logs: dict[str] = {}):
		train_accuracy = [
			value for key, value in logs.items()
			if 'accuracy' in key and 'val_' not in key
		]
		val_accuracy = [
			value for key, value in logs.items()
			if 'accuracy' in key and 'val_' in key
		]
		logs['accuracy'] = sum(train_accuracy) / len(train_accuracy)
		logs['val_accuracy'] = sum(val_accuracy) / len(val_accuracy)