from dataclasses import fields
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Singleton, Container

from core.tensorflow.tensorboard.service import TensorboardService
from core.tensorflow.device.service import DeviceService

from apps.magic_crystal.config import MagicCrystalConfig
from apps.magic_crystal.tuner.service import MagicCrystalTunerService
from apps.magic_crystal.preprocessor.service import MagicCrystalPreprocessorService
from apps.magic_crystal.trainer.service import MagicCrystalTrainerService
from apps.magic_crystal.predictor.service import MagicCrystalPredictorService
from apps.magic_crystal.dataset.sequence import MagicCrystalSequence
from apps.magic_crystal.dataset.service import MagicCrystalDatasetService
from apps.magic_crystal.model.service import MagicCrystalModelService
from apps.magic_crystal.strategy import MagicCrystalStrategy

class MagicCrystalModelContainer(DeclarativeContainer):
	config = Configuration()

	preprocessor_service = Singleton(
		MagicCrystalPreprocessorService,
		strategy_config = config.strategy,
	)
	sequence = Singleton(
		MagicCrystalSequence,
		strategy_config = config.strategy,
		preprocessor_service = preprocessor_service,
	)
	dataset_service = Singleton(
		MagicCrystalDatasetService,
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
		MagicCrystalTrainerService,
		config = config.trainer,
		strategy_config = config.strategy,
		tensorboard_service = tensorboard_service,
		device_service = device_service,
		dataset_service = dataset_service,
		artifacts_directory = config.artifacts_directory,
	)
	model_service = Singleton(
		MagicCrystalModelService,
		dataset_service = dataset_service,
		strategy_config = config.strategy
	)
	tuner_service = Singleton(
		MagicCrystalTunerService,
		config = config.tuner,
		model_service = model_service,
		device_service = device_service,
		trainer_service = trainer_service,
		tensorboard_service = tensorboard_service,
		artifacts_directory = config.artifacts_directory,
	)
	predictor_service = Singleton(
		MagicCrystalPredictorService,
		dataset_config = config.dataset,
		strategy_config = config.strategy,
		device_service = device_service,
		preprocessor_service = preprocessor_service,
	)

class MagicCrystalContainer(DeclarativeContainer):
	config = Configuration()
	model = Container(
		MagicCrystalModelContainer,
		config = config
	)

	strategy = Singleton(
		MagicCrystalStrategy,
		config = config.strategy,
		trainer_service = model.trainer_service,
		tuner_service = model.tuner_service,
		predictor_service = model.predictor_service,
	)

	def __new__(
		cls,
		*args,
		config: MagicCrystalConfig = None,
		**kwargs
	):
		if config == None:
			config = MagicCrystalConfig()
		container = super().__new__(cls, *args, **kwargs)

		for field in fields(config):
			getattr(container.config, field.name).from_value(getattr(config, field.name))

		return container
