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
from core.tensorflow.tuner.base.config import TunerConfig
from core.tensorflow.keras.callbacks import EarlyStoppingByModelSize

@dataclass
class TunerService(ArtifactService):
	model_service: 'ModelService' = None
	device_service: 'DeviceService' = None
	trainer_service: 'TrainerService' = None
	tensorboard_service: 'TensorboardService' = None
	tuner: Tuner = None
	config: TunerConfig = None

	@property
	def directory(self):
		return self.artifacts_directory.joinpath('tuner')

	@property
	def tuner_kwargs(self):
		def build(
			hyperparameters: HyperParameters
		):
			model = self.model_service.build(
				hyperparameters = hyperparameters
			)
			self.trainer_service.compile(
				model = model,
				hyperparameters = hyperparameters
			)
			return model

		return dict(
			hypermodel = build,
			objective = self.config.objective,
			directory = self.directory,
			project_name = type(self).__name__,
			max_model_size = self.config.model_size.max,
		)

	def get_callbacks(self, **kwargs):
		return self.tensorboard_service.get_callbacks(scope = type(self).__name__)

	def get_trial(self, trial_id: str or Literal['best']) -> Trial:
		if (trial_id == 'best'):
			trials = self.tuner.oracle.get_best_trials(1)
			if len(trials) == 0:
				return Trial(HyperParameters())
			else:
				return trials[0]
		return self.tuner.oracle.get_trial(trial_id)

	def get_hyperparameters(self, trial_id: str or Literal['best']) -> HyperParameters:
		return self.get_trial(trial_id).hyperparameters

	def get_model(self, trial_id: str or Literal['best']) -> Model:
		trial = self.get_trial(trial_id)
		hyperparameters = trial.hyperparameters
		model = self.model_service.build(
			hyperparameters = hyperparameters
		)
		model._name = trial.trial_id
		return model

	def tune(self):
		with self.device_service.selected_device:
			self.tuner.search(
				**self.trainer_service.train_kwargs,
				callbacks = self.get_callbacks()
			)