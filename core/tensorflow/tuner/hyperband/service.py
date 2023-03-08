from dataclasses import dataclass
from keras_tuner import Hyperband

from core.tensorflow.tuner.hyperband.config import HyperbandTunerConfig
from core.tensorflow.tuner.tuner.service import TunerService

@dataclass
class HyperbandTunerService(TunerService):
	config: HyperbandTunerConfig = None

	def __post_init__(self):
		self.tuner = Hyperband(
			hypermodel = self.model_service.compile,
			objective = 'val_loss',
			max_epochs = self.config.max_epochs,
			hyperband_iterations = self.config.iterations,
			factor = self.config.reduction_factor,
			directory = self.directory,
			project_name = type(self).__name__,
		)
