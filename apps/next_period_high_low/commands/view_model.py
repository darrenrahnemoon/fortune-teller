from argparse import ArgumentParser, Namespace
from apps.next_period_high_low.container import NextPeriodHighLowContainer

def config(parser: ArgumentParser):
	parser.add_argument('name', default = 'best')

def handler(args: Namespace):
	container = NextPeriodHighLowContainer.get()
	tuner_service = container.tuner_service()
	trainer_service = container.trainer_service()
	model = tuner_service.get_model(args.name)
	trainer_service.load_weights(model)
	model.summary()