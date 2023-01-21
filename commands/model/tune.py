from argparse import ArgumentParser, Namespace, BooleanOptionalAction
from shutil import rmtree

from ..utils.tensorboard import add_tensorboard_argument, ensure_tensorboard_running
from ..utils.cls import add_class_fields_as_arguments, setattr_from_args

from apps.next_period_high_low.container import NextPeriodHighLowContainer
from apps.next_period_high_low.config import NextPeriodHighLowConfiguration

def config(parser: ArgumentParser):
	add_tensorboard_argument(parser)
	add_class_fields_as_arguments(
		cls = NextPeriodHighLowConfiguration,
		parser = parser,
		recursive = [ 'model' ]
	)
	parser.add_argument('--clean', action = BooleanOptionalAction)

def handler(args: Namespace):
	config = NextPeriodHighLowConfiguration()
	setattr_from_args(config, args, recursive = [ 'model' ])

	container = NextPeriodHighLowContainer()
	container.config.from_pydantic(config)
	container.config.from_dict({
		'build_input_chart_group' : config.build_input_chart_group,
		'build_output_chart_group' : config.build_output_chart_group
	})

	strategy = container.strategy()

	if args.clean:
		rmtree(strategy.service.keras_tuner_directory, ignore_errors = True)
		rmtree(strategy.service.tensorboard_directory, ignore_errors = True)

	ensure_tensorboard_running(
		args,
		directory = strategy.service.tensorboard_directory
	)
	strategy.service.tune_model()