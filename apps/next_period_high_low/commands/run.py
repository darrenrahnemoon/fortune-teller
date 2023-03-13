from argparse import ArgumentParser, Namespace

import core.utils.command.config

from apps.next_period_high_low.container import NextPeriodHighLowContainer
from apps.next_period_high_low.config import NextPeriodHighLowConfig

def config(parser: ArgumentParser):
	core.utils.command.config.add_fields_to_arguments(parser, NextPeriodHighLowConfig)

def handler(args: Namespace):
	config = core.utils.command.config.set_fields_from_arguments(args, NextPeriodHighLowConfig())
	container = NextPeriodHighLowContainer(config = config)
	strategy = container.strategy()
	strategy.run()