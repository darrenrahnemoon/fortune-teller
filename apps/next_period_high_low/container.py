from dataclasses import fields
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Singleton, Container

from core.tensorflow.tensorboard.service import TensorboardService
from core.tensorflow.device.service import DeviceService

from apps.next_period_high_low.config import NextPeriodHighLowConfig

from apps.next_period_high_low.tuner import NextPeriodHighLowTunerService

from apps.next_period_high_low.preprocessor import NextPeriodHighLowPreprocessorService
from apps.next_period_high_low.trainer import NextPeriodHighLowTrainerService
from apps.next_period_high_low.predictor import NextPeriodHighLowPredictorService
from apps.next_period_high_low.dataset.sequence import NextPeriodHighLowSequence
from apps.next_period_high_low.dataset import NextPeriodHighLowDatasetService
from apps.next_period_high_low.model import NextPeriodHighLowModelService
from apps.next_period_high_low.strategy import NextPeriodHighLowStrategy

class NextPeriodHighLowModelContainer(DeclarativeContainer):
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
		NextPeriodHighLowDatasetService,
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
		NextPeriodHighLowTrainerService,
		config = config.trainer,
		strategy_config = config.strategy,
		tensorboard_service = tensorboard_service,
		device_service = device_service,
		dataset_service = dataset_service,
		artifacts_directory = config.artifacts_directory,
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
	predictor_service = Singleton(
		NextPeriodHighLowPredictorService,
		dataset_config = config.dataset,
		strategy_config = config.strategy,
		device_service = device_service,
		preprocessor_service = preprocessor_service,
	)

class NextPeriodHighLowContainer(DeclarativeContainer):
	config = Configuration()
	model = Container(
		NextPeriodHighLowModelContainer,
		config = config
	)

	strategy = Singleton(
		NextPeriodHighLowStrategy,
		config = config.strategy,
		trainer_service = model.trainer_service,
		tuner_service = model.tuner_service,
		predictor_service = model.predictor_service,
	)

	def __new__(
		cls,
		*args,
		config: NextPeriodHighLowConfig = None,
		**kwargs
	):
		if config == None:
			config = NextPeriodHighLowConfig()
		container = super().__new__(cls, *args, **kwargs)

		for field in fields(config):
			getattr(container.config, field.name).from_value(getattr(config, field.name))

		return container
