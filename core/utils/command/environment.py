from argparse import ArgumentParser, Namespace
import core.utils.environment as environment

def add_to_arguments(parser: ArgumentParser):
	parser.add_argument('--environment', choices = [ 'development', 'production' ], default = 'development')

def set_environment_from_arguments(args: Namespace):
	environment.stage = args.environment or environment.stage