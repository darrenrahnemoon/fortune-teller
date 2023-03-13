from argparse import ArgumentParser, Namespace, BooleanOptionalAction
from apps.next_period_high_low.container import NextPeriodHighLowContainer
from core.utils.os import open_file

def config(parser: ArgumentParser):
	parser.add_argument('model', choices = [ 'price', 'time' ])
	parser.add_argument('name', default = 'best')
	parser.add_argument('--plot', action = BooleanOptionalAction)

def handler(args: Namespace):
	container = NextPeriodHighLowContainer()
	container = getattr(container, args.model)()

	tuner_service = container.tuner_service()
	trainer_service = container.trainer_service()
	model = tuner_service.get_model(args.name)
	trainer_service.load_weights(model)
	model.summary()

	if args.plot:
		trainer_service.plot(model)
		path = trainer_service.get_plot_path(model)
		open_file(path)