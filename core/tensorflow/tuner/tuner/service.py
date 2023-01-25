from typing import TYPE_CHECKING
from dataclasses import dataclass
from keras import Model
from keras_tuner import Tuner, HyperParameters

if TYPE_CHECKING:
	from core.tensorflow.training.service import TrainingService
	from core.tensorflow.tensorboard.service import TensorboardService
	from core.tensorflow.device.service import DeviceService
	from core.tensorflow.model.service import ModelService
from core.tensorflow.artifact.service import ArtifactService

@dataclass
class TunerService(ArtifactService):
	model: 'ModelService' = None
	device: 'DeviceService' = None
	training: 'TrainingService' = None
	tensorboard: 'TensorboardService' = None

	@property
	def directory(self):
		return self.artifacts_directory.joinpath('tuner')

	@property
	def callbacks(self):
		return self.tensorboard.callbacks

	def create(self, *args, **kwargs) -> Tuner:
		pass

	def get_best_parameters(self) -> HyperParameters:
		tuner = self.create()
		return tuner.get_best_hyperparameters(1)[0]

	def get_best_model(self) -> Model:
		parameters = self.get_best_parameters()
		return self.model.build(parameters)

	def train_best_model(self):
		model = self.get_best_model()
		self.training.train(model)

	def predict_with_best_model(self, *args, **kwargs):
		model = self.get_best_model()
		return self.training.predict(model, *args, **kwargs)

	def tune(self):
		tuner = self.create()

		with self.device.selected:
			tuner.search(
				**self.training.train_arguments,
				callbacks = self.callbacks,
			)