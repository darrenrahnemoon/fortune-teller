from dependency_injector.providers import Configuration, Singleton
from dependency_injector.containers import DeclarativeContainer

from core.tensorflow.preprocessor.service import PreprocessorService
from core.tensorflow.dataset.service import DatasetService
from core.tensorflow.tensorboard.service import TensorboardService
from core.tensorflow.device.service import DeviceService
from core.tensorflow.model.service import ModelService
from core.tensorflow.tuner.base.service import TunerService
from core.tensorflow.predictor.service import PredictorService
from core.tensorflow.trainer.service import TrainerService

class TensorflowContainer(DeclarativeContainer):
	config = Configuration()

	preprocessor_service = Singleton(PreprocessorService)
	dataset_service = Singleton(
		DatasetService,
		config = config.dataset,
	)
	tensorboard_service = Singleton(
		TensorboardService,
		config = config.tensorboard,
		artifacts_directory = config.artifacts_directory
	)
	device_service = Singleton(
		DeviceService,
		config = config.device,
	)
	trainer_service = Singleton(
		TrainerService,
		config = config.trainer,
		tensorboard_service = tensorboard_service,
		device_service = device_service,
		dataset_service = dataset_service,
		artifacts_directory = config.artifacts_directory,
	)
	model_service = Singleton(
		ModelService,
		dataset_service = dataset_service,
	)
	tuner_service = Singleton(
		TunerService,
		config = config.tuner,
		model_service = model_service,
		device_service = device_service,
		trainer_service = trainer_service,
		tensorboard_service = tensorboard_service,
		artifacts_directory = config.artifacts_directory,
	)
	predictor_service = Singleton(
		PredictorService,
		dataset_config = config.dataset,
		device_service = device_service,
		preprocessor_service = preprocessor_service,
	)
