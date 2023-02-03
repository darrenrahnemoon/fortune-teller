from typing import Literal, TYPE_CHECKING
from dataclasses import dataclass
from keras import Model
from keras_tuner import Tuner, HyperParameters
from keras_tuner.engine.trial import Trial

if TYPE_CHECKING:
	from core.tensorflow.trainer.service import TrainerService
	from core.tensorflow.tensorboard.service import TensorboardService
	from core.tensorflow.device.service import DeviceService
	from core.tensorflow.model.service import ModelService
from core.tensorflow.artifact.service import ArtifactService

@dataclass
class TunerService(ArtifactService):
	model: 'ModelService' = None
	device: 'DeviceService' = None
	trainer: 'TrainerService' = None
	tensorboard: 'TensorboardService' = None

	@property
	def directory(self):
		return self.artifacts_directory.joinpath('tuner')

	@property
	def callbacks(self):
		return self.tensorboard.callbacks

	def create(self, *args, **kwargs) -> Tuner:
		pass

	def get_trial(self, trial_id: str or Literal['best']) -> Trial:
		tuner = self.create()
		if (trial_id == 'best'):
			return tuner.oracle.get_best_trials(1)
		return tuner.oracle.get_trial(trial_id)

	def get_hyperparameters(self, trial_id: str or Literal['best']) -> HyperParameters:
		return self.get_trial(trial_id).hyperparameters

	def get_model(self, trial_id: str or Literal['best']) -> Model:
		hyperparameters = self.get_hyperparameters(trial_id)
		return self.model.build(hyperparameters)

	def tune(self):
		tuner = self.create()
		self.tensorboard.ensure_running()
		with self.device.selected:
			tuner.search(
				**self.trainer.train_args,
				callbacks = self.callbacks,
			)