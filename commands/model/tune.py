from argparse import ArgumentParser, Namespace
from commands.utils.pydantic import add_configuration_as_arguments, get_overridden_configuration_from_arguments

from apps.next_period_high_low.container import NextPeriodHighLowContainer
from apps.next_period_high_low.config import NextPeriodHighLowConfig

def config(parser: ArgumentParser):
	add_configuration_as_arguments(parser, NextPeriodHighLowConfig)

def handler(args: Namespace):
	config = get_overridden_configuration_from_arguments(args, NextPeriodHighLowConfig)
	container = NextPeriodHighLowContainer.get(config = config)
	tuner = container.tuner()
	tuner.tune()