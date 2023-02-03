from argparse import ArgumentParser, Namespace
from core.utils.environment import stage

def add_args(parser: ArgumentParser):
	parser.add_argument('--stage', choices = [ 'training', 'tuning', 'production' ], default = 'training')

def set_stage_from_args(args: Namespace):
	stage.set(args.stage)