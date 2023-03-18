from argparse import ArgumentParser
from core.utils.logging import logging, loggers
from core.utils.logging.filter import MessageFilter

def add_to_arguments(parser: ArgumentParser):
	parser.add_argument('--log-level', '-l', choices = [ 'CRITICAL', 'FATAL', 'ERROR', 'WARNING', 'WARN', 'INFO', 'DEBUG' ])
	parser.add_argument('--log-filter', nargs = '+', type = str, default = [])

def set_log_level_from_arguments(args):
	if args.log_level:
		logging.root.setLevel(args.log_level)
	if len(args.log_filter):
		filter = MessageFilter(args.log_filter)
		logging.root.addFilter(filter)
		for logger in loggers:
			logger.addFilter(filter)