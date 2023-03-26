from keras import Model
from core.tensorflow.preprocessor.service import PreprocessorService

class PredictorService:
	preprocessor_service: PreprocessorService = None

	def predict(self, model: Model, *args, **kwargs):
		pass