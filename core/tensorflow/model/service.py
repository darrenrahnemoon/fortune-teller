from dataclasses import dataclass
from keras_tuner import HyperParameters
from core.tensorflow.dataset.service import DatasetService

@dataclass
class ModelService:
	dataset: DatasetService = None

	def build(parameters: HyperParameters):
		pass