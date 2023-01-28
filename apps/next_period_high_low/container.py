from dataclasses import asdict

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Singleton

from core.tensorflow.tensorboard.service import TensorboardService
from core.tensorflow.device.service import DeviceService
from core.tensorflow.dataset.service import DatasetService
from core.tensorflow.tuner.hyperband.service import HyperbandTunerService

from .trainer import NextPeriodHighLowTrainerService
from .config import NextPeriodHighLowConfig
from .preprocessor import NextPeriodHighLowPreprocessor
from .sequence import NextPeriodHighLowSequence
from .model import NextPeriodHighLowModelService
from .strategy import NextPeriodHighLowStrategy

class NextPeriodHighLowContainer(DeclarativeContainer):
	config = Configuration()

	preprocessor = Singleton(
		NextPeriodHighLowPreprocessor,
		strategy_config = config.strategy,
	)
	sequence = Singleton(
		NextPeriodHighLowSequence,
		strategy_config = config.strategy,
		preprocessor = preprocessor,
	)
	dataset = Singleton(
		DatasetService,
		config = config.dataset,
		dataset = sequence,
	)
	tensorboard = Singleton(
		TensorboardService,
		config = config.tensorboard,
		artifacts_directory = config.artifacts_directory
	)
	device = Singleton(
		DeviceService,
		config = config.device,
	)
	trainer = Singleton(
		NextPeriodHighLowTrainerService,
		config = config.trainer,
		strategy_config = config.strategy,
		tensorboard = tensorboard,
		device = device,
		dataset = dataset,
		artifacts_directory = config.artifacts_directory,
		preprocessor = preprocessor
	)
	model = Singleton(
		NextPeriodHighLowModelService,
		dataset = dataset,
		strategy_config = config.strategy
	)
	tuner = Singleton(
		HyperbandTunerService,
		config = config.tuner,
		model = model,
		device = device,
		trainer = trainer,
		tensorboard = tensorboard,
		artifacts_directory = config.artifacts_directory,
	)
	strategy = Singleton(
		NextPeriodHighLowStrategy,
		config = config.strategy,
		trainer = trainer,
		tuner = tuner,
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
		container.config.dataset.from_value(config.dataset)
		container.config.device.from_value(config.device)
		container.config.tensorboard.from_value(config.tensorboard)
		container.config.trainer.from_value(config.trainer)
		container.config.tuner.from_value(config.tuner)
		container.config.strategy.from_value(config.strategy)
		container.config.artifacts_directory.from_value(config.artifacts_directory)
		return container
