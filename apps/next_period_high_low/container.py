from pathlib import Path

from core.tensorflow.tensorboard.service import TensorboardService
from core.tensorflow.device.service import DeviceService
from core.tensorflow.dataset.service import DatasetService
from core.tensorflow.training.service import TrainingService
from core.tensorflow.tuner.hyperband.service import HyperbandTunerService

from apps.next_period_high_low.config import NextPeriodHighLowConfig
from apps.next_period_high_low.preprocessor import NextPeriodHighLowPreprocessor
from apps.next_period_high_low.sequence import NextPeriodHighLowSequence
from apps.next_period_high_low.model import NextPeriodHighLowModelService
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Singleton

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
	training = Singleton(
		TrainingService,
		config = config.training,
		tensorboard = tensorboard,
		device = device,
		dataset = dataset,
		artifacts_directory = config.artifacts_directory,
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
		training = training,
		tensorboard = tensorboard,
		artifacts_directory = config.artifacts_directory,
	)

	@classmethod
	def get(
		cls,
		*args,
		config: NextPeriodHighLowConfig = NextPeriodHighLowConfig(),
		**kwargs
	):
		container = cls(*args, **kwargs)
		container.config.dataset.from_value(config.dataset)
		container.config.device.from_value(config.device)
		container.config.tensorboard.from_value(config.tensorboard)
		container.config.training.from_value(config.training)
		container.config.tuner.from_value(config.tuner)
		container.config.strategy.from_value(config.strategy)
		container.config.artifacts_directory.from_value(config.artifacts_directory)
		return container
