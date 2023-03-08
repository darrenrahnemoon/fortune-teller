from dataclasses import dataclass
from keras import Model
from keras_tuner import HyperParameters
from core.tensorflow.dataset.service import DatasetService

@dataclass
class ModelService:
	dataset_service: DatasetService = None

	def build(self, parameters: HyperParameters) -> Model:
		pass

	def compile(self, parameters: HyperParameters) -> Model:
		pass