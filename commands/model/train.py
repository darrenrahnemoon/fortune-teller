from argparse import ArgumentParser, Namespace

from apps.next_period_high_low.container import NextPeriodHighLowContainer
from apps.next_period_high_low.config import NextPeriodHighLowConfig
import commands.utils.config

def config(parser: ArgumentParser):
	commands.utils.config.add_args(parser, NextPeriodHighLowConfig)

def handler(args: Namespace):
	config = commands.utils.config.set_fields_from_args(args, NextPeriodHighLowConfig())
	container = NextPeriodHighLowContainer.get(config = config)

	tuner = container.tuner()
	trainer = container.trainer()
	model = tuner.get_model(trainer.config.trial)

	trainer.load_weights(model)
	trainer.train(model)