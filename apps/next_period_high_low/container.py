from pathlib import Path

from core.tensorflow.tensorboard.service import TensorboardService
from core.tensorflow.device.service import DeviceService
from core.tensorflow.dataset.service import DatasetService
from core.tensorflow.training.service import TrainingService
from core.tensorflow.tuner.hyperband.service import HyperbandTunerService

from apps.next_period_high_low.config import NextPeriodHighLowConfiguration
from apps.next_period_high_low.preprocessor import NextPeriodHighLowPreprocessor
from apps.next_period_high_low.sequence import NextPeriodHighLowSequence
from apps.next_period_high_low.model import NextPeriodHighLowModelService
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Singleton

artifacts_directory = Path('./apps/next_period_high_low/artifacts')

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
		artifacts_directory = artifacts_directory
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
	)
	model = Singleton(
		NextPeriodHighLowModelService,
		training = training,
		strategy_config = config.strategy
	)
	tuner = Singleton(
		HyperbandTunerService,
		config = config.tuner,
		model = model,
		device = device,
		training = training,
		tensorboard = tensorboard,
	)

	@classmethod
	def get(
		cls,
		*args,
		config: NextPeriodHighLowConfiguration = NextPeriodHighLowConfiguration(),
		**kwargs
	):
		container = cls(*args, **kwargs)
		container.config.from_pydantic(config)
		container.config.strategy.from_dict({
			'build_input_chart_group' : config.build_input_chart_group,
			'build_output_chart_group' : config.build_output_chart_group
		})
		return container
