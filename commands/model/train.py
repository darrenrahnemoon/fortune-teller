from argparse import ArgumentParser, Namespace, BooleanOptionalAction
from shutil import rmtree

from commands.utils.tensorboard import add_tensorboard_argument, ensure_tensorboard_running
from commands.utils.pydantic import add_configuration_as_arguments, get_overridden_configuration_from_arguments

from apps.next_period_high_low.container import NextPeriodHighLowContainer
from apps.next_period_high_low.config import NextPeriodHighLowConfiguration

def config(parser: ArgumentParser):
	add_tensorboard_argument(parser)
	add_configuration_as_arguments(parser, NextPeriodHighLowConfiguration)

def handler(args: Namespace):
	config = get_overridden_configuration_from_arguments(args, NextPeriodHighLowConfiguration)
	container = NextPeriodHighLowContainer.get(config = config)
	service = container.service()

	ensure_tensorboard_running(args, service.tensorboard_directory)
	service.train_model()