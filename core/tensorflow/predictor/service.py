from dataclasses import dataclass
from keras import Model

from core.tensorflow.dataset.config import DatasetConfig
from core.tensorflow.preprocessor.service import PreprocessorService
from core.tensorflow.device.service import DeviceService

@dataclass
class PredictorService:
	device_service: DeviceService = None
	dataset_config: DatasetConfig = None
	preprocessor_service: PreprocessorService = None

	def predict(self, model: Model, *args, **kwargs):
		pass