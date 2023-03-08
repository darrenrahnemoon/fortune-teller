from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Singleton

from core.tensorflow.tensorboard.service import TensorboardService
from core.tensorflow.device.service import DeviceService
from core.tensorflow.dataset.service import DatasetService

from .tuner import NextPeriodHighLowTunerService
from .trainer import NextPeriodHighLowTrainerService
from .config import NextPeriodHighLowConfig
from .preprocessor import NextPeriodHighLowPreprocessorService
from .sequence import NextPeriodHighLowSequence
from .model import NextPeriodHighLowModelService
from .strategy import NextPeriodHighLowStrategy

class NextPeriodHighLowContainer(DeclarativeContainer):
	config = Configuration()

	preprocessor_service = Singleton(
		NextPeriodHighLowPreprocessorService,
		strategy_config = config.strategy,
	)
	sequence = Singleton(
		NextPeriodHighLowSequence,
		strategy_config = config.strategy,
		preprocessor_service = preprocessor_service,
	)
	dataset_service = Singleton(
		DatasetService,
		config = config.dataset,
		dataset = sequence,
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
		NextPeriodHighLowTrainerService,
		config = config.trainer,
		strategy_config = config.strategy,
		tensorboard_service = tensorboard_service,
		device_service = device_service,
		dataset_service = dataset_service,
		artifacts_directory = config.artifacts_directory,
		preprocessor_service = preprocessor_service
	)
	model_service = Singleton(
		NextPeriodHighLowModelService,
		dataset_service = dataset_service,
		strategy_config = config.strategy
	)
	tuner_service = Singleton(
		NextPeriodHighLowTunerService,
		config = config.tuner,
		model_service = model_service,
		device_service = device_service,
		trainer_service = trainer_service,
		tensorboard_service = tensorboard_service,
		artifacts_directory = config.artifacts_directory,
	)
	strategy = Singleton(
		NextPeriodHighLowStrategy,
		config = config.strategy,
		trainer_service = trainer_service,
		tuner_service = tuner_service,
	)

	@classmethod
	def get(
		cls,
		*args,
		config: NextPeriodHighLowConfig = None,
		**kwargs
	):
		if config == None:
			config = NextPeriodHighLowConfig()
		container = cls(*args, **kwargs)
		container.config.artifacts_directory.from_value(config.artifacts_directory)
		container.config.dataset.from_value(config.dataset)
		container.config.device.from_value(config.device)
		container.config.tensorboard.from_value(config.tensorboard)
		container.config.trainer.from_value(config.trainer)
		container.config.tuner.from_value(config.tuner)
		container.config.strategy.from_value(config.strategy)
		return container
