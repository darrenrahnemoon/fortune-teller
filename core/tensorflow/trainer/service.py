from dataclasses import dataclass
from shutil import rmtree

from keras import Model
from keras.utils import plot_model
from keras.callbacks import ModelCheckpoint

from core.tensorflow.trainer.config import TrainerConfig
from core.tensorflow.dataset.service import DatasetService
from core.tensorflow.device.service import DeviceService
from core.tensorflow.tensorboard.service import TensorboardService
from core.tensorflow.artifact.service import ArtifactService
from core.utils.logging import logging

logger = logging.getLogger(__name__)

@dataclass
class TrainerService(ArtifactService):
	config: TrainerConfig = None
	tensorboard_service: TensorboardService = None
	device_service: DeviceService = None
	dataset_service: DatasetService = None

	@property
	def directory(self):
		return self.artifacts_directory.joinpath('trainer', type(self).__name__)

	def get_checkpoints_path(self, model: Model):
		return self.directory.joinpath(model.name, 'checkpoints')

	def get_plot_path(self, model: Model):
		return self.directory.joinpath(model.name, 'plot.png')

	def get_callbacks(self, model: Model):
		callbacks = [
			ModelCheckpoint(
				filepath = self.get_checkpoints_path(model),
				save_weights_only = True,
				monitor = 'val_loss',
				mode = 'min',
			)
		]
		return callbacks + self.tensorboard_service.get_callbacks(
			scope = type(self).__name__
		)

	@property
	def train_kwargs(self):
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
		checkpoints_path = self.get_checkpoints_path(model)
		try:
			model.load_weights(str(checkpoints_path))
		except:
			logger.warn(f"Unable to load weights for model '{model.name}' from path '{checkpoints_path}'")

	def compile(self, model: Model):
		pass

	def train(self, model: Model):
		if self.config.overwrite:
			rmtree(self.get_checkpoints_path(model).parent, ignore_errors = True)

		with self.device_service.selected_device:
			model.fit(
				**self.train_kwargs,
				callbacks = self.get_callbacks(model)
			)

	def plot(self, model: Model):
		path = self.get_plot_path(model)
		path.parent.mkdir(exist_ok = True)
		plot_model(
			model,
			to_file = path,
			show_shapes = True,
			show_dtype = True,
			show_layer_activations = True,
		)

	def predict(self, model: Model, *args, **kwargs):
		pass