from dataclasses import dataclass
from keras_tuner import HyperParameters
from core.tensorflow.training.service import TrainingService

@dataclass
class ModelService:
	training: TrainingService = None

	def build(parameters: HyperParameters):
		pass