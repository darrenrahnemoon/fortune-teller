from dependency_injector.providers import Singleton, Configuration

from core.tensorflow.container import TensorflowContainer
from examples.ave_maria.tensorflow.preprocessor.service import AveMariaPreprocessorService
from examples.ave_maria.tensorflow.dataset.service import AveMariaDatasetService
from examples.ave_maria.tensorflow.trainer.service import AveMariaTrainerService
from examples.ave_maria.tensorflow.predictor.service import AveMariaPredictorService
from examples.ave_maria.tensorflow.tuner.service import AveMariaTunerService
from examples.ave_maria.tensorflow.model.service import AveMariaModelService

class AveMariaTensorflowContainer(TensorflowContainer):
	trading_config = Configuration()

	preprocessor_service = Singleton(
		AveMariaPreprocessorService,
		trading_config = trading_config.raw,
	)
	dataset_service = Singleton(
		AveMariaDatasetService,
		config = TensorflowContainer.config.dataset,
		trading_config = trading_config.raw,
		preprocessor_service = preprocessor_service,
	)
	trainer_service = Singleton(
		AveMariaTrainerService,
		config = TensorflowContainer.config.trainer,
		trading_config = trading_config.raw,
		tensorboard_service = TensorflowContainer.tensorboard_service,
		device_service = TensorflowContainer.device_service,
		dataset_service = dataset_service,
		artifacts_directory = TensorflowContainer.config.artifacts_directory,
	)
	model_service = Singleton(
		AveMariaModelService,
		dataset_service = dataset_service,
		trading_config = trading_config.raw,
	)
	tuner_service = Singleton(
		AveMariaTunerService,
		config = TensorflowContainer.config.tuner,
		model_service = model_service,
		device_service = TensorflowContainer.device_service,
		trainer_service = trainer_service,
		tensorboard_service = TensorflowContainer.tensorboard_service,
		artifacts_directory = TensorflowContainer.config.artifacts_directory,
	)
	predictor_service = Singleton(
		AveMariaPredictorService,
		dataset_config = TensorflowContainer.config.dataset,
		trading_config = TensorflowContainer.config.trading,
		device_service = TensorflowContainer.device_service,
		preprocessor_service = preprocessor_service,
	)
