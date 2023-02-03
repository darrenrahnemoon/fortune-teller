from dataclasses import dataclass

from keras import Model
from keras.callbacks import ModelCheckpoint

from core.tensorflow.trainer.config import TrainerConfig
from core.tensorflow.dataset.service import DatasetService
from core.tensorflow.device.service import DeviceService
from core.tensorflow.tensorboard.service import TensorboardService
from core.tensorflow.artifact.service import ArtifactService

@dataclass
class TrainerService(ArtifactService):
	config: TrainerConfig = None
	tensorboard_service: TensorboardService = None
	device_service: DeviceService = None
	dataset_service: DatasetService = None

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
		return callbacks + self.tensorboard_service.callbacks

	@property
	def train_args(self):
		training_dataset, validation_dataset = self.dataset_service.get()
		return dict(
			x = training_dataset,
			validation_data = validation_dataset,
			epochs = self.config.epochs,
			steps_per_epoch = self.config.steps_per_epoch,
			batch_size = self.dataset_service.config.batch_size,
			validation_batch_size = self.dataset_service.config.batch_size,
			validation_steps = int(self.config.steps_per_epoch / (1 - self.dataset_service.config.validation_split) * self.dataset_service.config.validation_split),
			verbose = True
		)

	def load_weights(self, model: Model):
		if self.directory.exists():
			model.load_weights(self.directory)

	def train(self, model: Model):
		self.tensorboard_service.ensure_running()

		with self.device_service.selected_device:
			model.fit(
				callbacks = self.callbacks,
				**self.train_args,
			)

	def predict(self, model: Model, *args, **kwargs):
		pass