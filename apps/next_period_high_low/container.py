from apps.next_period_high_low.config import NextPeriodHighLowConfiguration
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Factory

from .strategy import NextPeriodHighLowStrategy
from .model.model import NextPeriodHighLowModel
from .model.preprocessor import NextPeriodHighLowPreprocessor
from .model.sequence import NextPeriodHighLowSequence
from .model.service import NextPeriodHighLowService

class NextPeriodHighLowContainer(DeclarativeContainer):
	config = Configuration()

	model = Factory(
		NextPeriodHighLowModel,
		build_input_chart_group = config.build_input_chart_group,
		build_output_chart_group = config.build_output_chart_group,
		forward_window_length = config.forward_window_length,
		backward_window_length = config.backward_window_length,

		batch_size = config.model.batch_size,
	)

	preprocessor = Factory(
		NextPeriodHighLowPreprocessor,
		forward_window_length = config.forward_window_length,
		backward_window_length = config.backward_window_length,
	)

	dataset = Factory(
		NextPeriodHighLowSequence,
		build_input_chart_group = config.build_input_chart_group,
		build_output_chart_group = config.build_output_chart_group,
		backward_window_length = config.backward_window_length,
		forward_window_length = config.forward_window_length,

		repository = config.model.repository,
		preprocessor = preprocessor,
	)

	service = Factory(
		NextPeriodHighLowService,
		build_input_chart_group = config.build_input_chart_group,
		build_output_chart_group = config.build_output_chart_group,
		forward_window_length = config.forward_window_length,
		backward_window_length = config.backward_window_length,

		validation_split = config.model.validation_split,
		batch_size = config.model.batch_size,
		epochs = config.model.epochs,
		steps_per_epoch = config.model.steps_per_epoch,
		hyperband_max_epochs = config.model.hyperband_max_epochs,
		hyperband_reduction_factor = config.model.hyperband_reduction_factor,
		hyperband_iterations = config.model.hyperband_iterations,
		use_multiprocessing = config.model.use_multiprocessing,
		max_queue_size = config.model.max_queue_size,
		workers = config.model.workers,
		use_device = config.model.use_device,

		preprocessor = preprocessor,
		model = model,
		dataset = dataset,
	)

	strategy = Factory(
		NextPeriodHighLowStrategy,
		metatrader_repository = config.metatrader_repository,
		alphavantage_repository = config.alphavantage_repository,
		forward_window_length = config.forward_window_length,
		backward_window_length = config.backward_window_length,
		build_input_chart_group = config.build_input_chart_group,
		build_output_chart_group = config.build_output_chart_group,

		service = service,
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
		container.config.from_dict({
			'build_input_chart_group' : config.build_input_chart_group,
			'build_output_chart_group' : config.build_output_chart_group
		})
		container.wire
		return container
