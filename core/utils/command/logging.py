from argparse import ArgumentParser
from core.utils.logging import logging

def add_to_arguments(parser: ArgumentParser):
	parser.add_argument('--log-level', '-l', choices = [ 'CRITICAL', 'FATAL', 'ERROR', 'WARNING', 'WARN', 'INFO', 'DEBUG' ])

def set_log_level_from_arguments(args):
	if args.log_level:
		logging.root.setLevel(args.log_level)