from argparse import ArgumentParser, Namespace
from core.utils.environment import stage

def add_to_arguments(parser: ArgumentParser):
	parser.add_argument('--stage', choices = [ 'training', 'tuning', 'production' ], default = 'training')

def set_stage_from_arguments(args: Namespace):
	stage.set(args.stage)