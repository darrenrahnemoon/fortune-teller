from argparse import ArgumentParser, Namespace

from apps.next_period_high_low.container import NextPeriodHighLowContainer
from apps.next_period_high_low.config import NextPeriodHighLowConfig
import commands.utils.config

def config(parser: ArgumentParser):
	commands.utils.config.add_args(parser, NextPeriodHighLowConfig)

def handler(args: Namespace):
	config = commands.utils.config.set_fields_from_args(args, NextPeriodHighLowConfig())
	container = NextPeriodHighLowContainer.get(config = config)

	tuner_service = container.tuner_service()
	trainer_service = container.trainer_service()
	model = tuner_service.get_model(trainer_service.config.trial)

	trainer_service.load_weights(model)
	trainer_service.train(model)