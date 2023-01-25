from dataclasses import dataclass
from typing import TYPE_CHECKING

from keras import Model
from keras.callbacks import ModelCheckpoint

from core.tensorflow.training.config import TrainingConfig
from core.tensorflow.dataset.service import DatasetService
from core.tensorflow.device.service import DeviceService
from core.tensorflow.tensorboard.service import TensorboardService
from core.tensorflow.artifact.service import ArtifactService

@dataclass
class TrainingService(ArtifactService):
	config: TrainingConfig = None
	tensorboard: TensorboardService = None
	device: DeviceService = None
	dataset: DatasetService = None

	@property
	def directory(self):
		return self.artifacts_directory.joinpath('checkpoints/checkpoints')

	@property
	def callbacks(self):
		callbacks = [
			ModelCheckpoint(
				filepath = self.directory,
				save_weights_only = True,
				monitor = 'val_loss',
				mode = 'max',
				save_best_only = True,
			)
		]
		return callbacks + self.tensorboard.callbacks

	@property
	def train_arguments(self):
		training_dataset, validation_dataset = self.dataset.get()
		return dict(
			x = training_dataset,
			validation_data = validation_dataset,
			epochs = self.config.epochs,
			steps_per_epoch = self.config.steps_per_epoch,
			batch_size = self.dataset.config.batch_size,
			validation_batch_size = self.dataset.config.batch_size,
			validation_steps = int(self.config.steps_per_epoch / (1 - self.dataset.config.validation_split) * self.dataset.config.validation_split),
			verbose = True
		)

	def train(self, model: Model):
		if self.directory.exists():
			model.load_weights(self.directory)

		with self.device.selected:
			model.fit(
				callbacks = self.callbacks,
				**self.train_arguments,
			)

	def predict(self, model: Model):
		pass