from dataclasses import dataclass
from keras_tuner import RandomSearch

from core.tensorflow.tuner.random.config import RandomSearchTunerConfig
from core.tensorflow.tuner.base.service import TunerService

@dataclass
class RandomSearchTunerService(TunerService):
	config: RandomSearchTunerConfig = None

	def __post_init__(self):
		self.tuner = RandomSearch(
			**self.tuner_kwargs
		)
