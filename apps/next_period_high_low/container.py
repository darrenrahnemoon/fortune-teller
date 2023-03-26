from dataclasses import fields
from dependency_injector.containers import DeclarativeContainer, copy
from dependency_injector.providers import Configuration, Singleton, Container

from core.tensorflow.tensorboard.service import TensorboardService
from core.tensorflow.device.service import DeviceService

from apps.next_period_high_low.config import NextPeriodHighLowConfig

from apps.next_period_high_low.tuner.price import NextPeriodHighLowPriceTunerService
from apps.next_period_high_low.tuner.time import NextPeriodHighLowTimeTunerService

from apps.next_period_high_low.preprocessor.price import NextPeriodHighLowPricePreprocessorService
from apps.next_period_high_low.preprocessor.time import NextPeriodHighLowTimePreprocessorService

from apps.next_period_high_low.trainer.price import NextPeriodHighLowPriceTrainerService
from apps.next_period_high_low.trainer.time import NextPeriodHighLowTimeTrainerService

from apps.next_period_high_low.predictor.price import NextPeriodHighLowPricePredictorService
from apps.next_period_high_low.predictor.time import NextPeriodHighLowTimePredictorService

from apps.next_period_high_low.dataset.sequence import NextPeriodHighLowSequence
from apps.next_period_high_low.dataset import NextPeriodHighLowDatasetService

from apps.next_period_high_low.model.price import NextPeriodHighLowPriceModelService
from apps.next_period_high_low.model.time import NextPeriodHighLowTimeModelService

from apps.next_period_high_low.strategy import NextPeriodHighLowStrategy

class NextPeriodHighLowPriceContainer(DeclarativeContainer):
	config = Configuration()

	preprocessor_service = Singleton(
		NextPeriodHighLowPricePreprocessorService,
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
		NextPeriodHighLowPriceTrainerService,
		config = config.trainer,
		strategy_config = config.strategy,
		tensorboard_service = tensorboard_service,
		device_service = device_service,
		dataset_service = dataset_service,
		artifacts_directory = config.artifacts_directory,
		preprocessor_service = preprocessor_service
	)
	model_service = Singleton(
		NextPeriodHighLowPriceModelService,
		dataset_service = dataset_service,
		strategy_config = config.strategy
	)
	tuner_service = Singleton(
		NextPeriodHighLowPriceTunerService,
		config = config.tuner,
		model_service = model_service,
		device_service = device_service,
		trainer_service = trainer_service,
		tensorboard_service = tensorboard_service,
		artifacts_directory = config.artifacts_directory,
	)
	predictor_service = Singleton(
		NextPeriodHighLowPricePredictorService,
		preprocessor_service = preprocessor_service,
	)

@copy(NextPeriodHighLowPriceContainer)
class NextPeriodHighLowTimeContainer(NextPeriodHighLowPriceContainer):
	def __new__(cls, *args, **kwargs):
		container = super().__new__(cls, *args, **kwargs)
		container.preprocessor_service.override(
			Singleton(
				NextPeriodHighLowTimePreprocessorService,
				strategy_config = container.config.strategy
			)
		)
		container.model_service.override(
			Singleton(
				NextPeriodHighLowTimeModelService,
				strategy_config = container.config.strategy,
				dataset_service = container.dataset_service
			)
		)
		container.trainer_service.override(
			Singleton(
				NextPeriodHighLowTimeTrainerService,
				config = container.config.trainer,
				strategy_config = container.config.strategy,
				tensorboard_service = container.tensorboard_service,
				device_service = container.device_service,
				dataset_service = container.dataset_service,
				artifacts_directory = container.config.artifacts_directory,
				preprocessor_service = container.preprocessor_service
			)
		)
		container.tuner_service.override(
			Singleton(
				NextPeriodHighLowTimeTunerService,
				config = container.config.tuner,
				model_service = container.model_service,
				device_service = container.device_service,
				trainer_service = container.trainer_service,
				tensorboard_service = container.tensorboard_service,
				artifacts_directory = container.config.artifacts_directory,
			)
		)
		container.predictor_service.override(
			Singleton(
				NextPeriodHighLowPricePredictorService,
				preprocessor_service = container.preprocessor_service,
			)
		)
		return container

class NextPeriodHighLowContainer(DeclarativeContainer):
	config = Configuration()
	price = Container(
		NextPeriodHighLowPriceContainer,
		config = config
	)
	time = Container(
		NextPeriodHighLowTimeContainer,
		config = config,
	)
	strategy = Singleton(
		NextPeriodHighLowStrategy,
		config = config.strategy,
		price_trainer_service = price.trainer_service,
		price_tuner_service = price.tuner_service,
		price_predictor_service = price.predictor_service,
		time_trainer_service = time.trainer_service,
		time_tuner_service = time.tuner_service,
		time_predictor_service = time.predictor_service,
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
