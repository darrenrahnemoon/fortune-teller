from dataclasses import fields
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Singleton, Container

from core.tensorflow.tensorboard.service import TensorboardService
from core.tensorflow.device.service import DeviceService

from apps.pelosi_predictor.config import PelosiPredictorConfig
from apps.pelosi_predictor.tuner.service import PelosiPredictorTunerService
from apps.pelosi_predictor.preprocessor.service import PelosiPredictorPreprocessorService
from apps.pelosi_predictor.trainer.service import PelosiPredictorTrainerService
from apps.pelosi_predictor.predictor.service import PelosiPredictorPredictorService
from apps.pelosi_predictor.dataset.sequence import PelosiPredictorSequence
from apps.pelosi_predictor.dataset.service import PelosiPredictorDatasetService
from apps.pelosi_predictor.model.service import PelosiPredictorModelService
from apps.pelosi_predictor.strategy import PelosiPredictorStrategy

class PelosiPredictorModelContainer(DeclarativeContainer):
	config = Configuration()

	preprocessor_service = Singleton(
		PelosiPredictorPreprocessorService,
		strategy_config = config.strategy,
	)
	sequence = Singleton(
		PelosiPredictorSequence,
		strategy_config = config.strategy,
		preprocessor_service = preprocessor_service,
	)
	dataset_service = Singleton(
		PelosiPredictorDatasetService,
		config = config.dataset,
		sequence = sequence,
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
		PelosiPredictorTrainerService,
		config = config.trainer,
		strategy_config = config.strategy,
		tensorboard_service = tensorboard_service,
		device_service = device_service,
		dataset_service = dataset_service,
		artifacts_directory = config.artifacts_directory,
	)
	model_service = Singleton(
		PelosiPredictorModelService,
		dataset_service = dataset_service,
		strategy_config = config.strategy
	)
	tuner_service = Singleton(
		PelosiPredictorTunerService,
		config = config.tuner,
		model_service = model_service,
		device_service = device_service,
		trainer_service = trainer_service,
		tensorboard_service = tensorboard_service,
		artifacts_directory = config.artifacts_directory,
	)
	predictor_service = Singleton(
		PelosiPredictorPredictorService,
		dataset_config = config.dataset,
		strategy_config = config.strategy,
		device_service = device_service,
		preprocessor_service = preprocessor_service,
	)

class PelosiPredictorContainer(DeclarativeContainer):
	config = Configuration()
	model = Container(
		PelosiPredictorModelContainer,
		config = config
	)

	strategy = Singleton(
		PelosiPredictorStrategy,
		config = config.strategy,
		trainer_service = model.trainer_service,
		tuner_service = model.tuner_service,
		predictor_service = model.predictor_service,
	)

	def __new__(
		cls,
		*args,
		config: PelosiPredictorConfig = None,
		**kwargs
	):
		if config == None:
			config = PelosiPredictorConfig()
		container = super().__new__(cls, *args, **kwargs)

		for field in fields(config):
			getattr(container.config, field.name).from_value(getattr(config, field.name))

		return container
