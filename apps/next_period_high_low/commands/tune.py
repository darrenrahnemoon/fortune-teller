from argparse import ArgumentParser, Namespace

from apps.next_period_high_low.container import NextPeriodHighLowContainer
from apps.next_period_high_low.config import NextPeriodHighLowConfig
import core.utils.command.config

def config(parser: ArgumentParser):
	core.utils.command.config.add_fields_to_arguments(parser, NextPeriodHighLowConfig)

def handler(args: Namespace):
	config = core.utils.command.config.set_fields_from_arguments(args, NextPeriodHighLowConfig())
	container = NextPeriodHighLowContainer.get(config = config)
	tuner_service = container.tuner_service()
	tuner_service.tune()