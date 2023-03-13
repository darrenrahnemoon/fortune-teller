from argparse import ArgumentParser, Namespace
from apps.next_period_high_low.container import NextPeriodHighLowContainer
from apps.next_period_high_low.config import NextPeriodHighLowConfig
import core.utils.command.config
from core.utils.cls import pretty_repr

def config(parser: ArgumentParser):
	parser.add_argument('model', choices = [ 'price', 'time' ])
	core.utils.command.config.add_fields_to_arguments(parser, NextPeriodHighLowConfig)

def handler(args: Namespace):
	config = core.utils.command.config.set_fields_from_arguments(args, NextPeriodHighLowConfig())
	container = NextPeriodHighLowContainer(config = config)
	container = getattr(container, args.model)()

	tuner_service = container.tuner_service()
	trainer_service = container.trainer_service()
	model = tuner_service.get_model(trainer_service.config.trial)
	model.summary()
	parameters = tuner_service.get_hyperparameters(trainer_service.config.trial)
	print(pretty_repr(parameters.values))
	trainer_service.compile(model, parameters)
	trainer_service.load_weights(model)
	trainer_service.train(model)