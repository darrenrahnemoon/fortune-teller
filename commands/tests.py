from argparse import ArgumentParser, Namespace, BooleanOptionalAction
from core.utils.test import TestManager

def config(parser: ArgumentParser):
	parser.add_argument('--patterns', nargs = '*', default = [ 'tests/**/*.py' ])
	parser.add_argument('--filter', '-f', type = str, default = '')

def handler(args: Namespace):
	TestManager.load_from_files(args.patterns)
	TestManager.run_all(args.filter)