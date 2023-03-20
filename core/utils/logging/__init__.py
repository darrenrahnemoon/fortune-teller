import os
import sys
import logging
from logging_json import JSONFormatter
from core.utils.time import now
from core.utils.environment import project_directory
from .formatter import ColoredFormatter

stdout_stream = logging.StreamHandler(sys.stdout)
stdout_stream.formatter = ColoredFormatter(
	colored_format = '[%(process)d][%(asctime)s][%(levelname)s][%(name)s][%(funcName)s]:\n',
	uncolored_format = '%(message)s\n'
)

file_stream = logging.FileHandler(project_directory.joinpath(f"core/artifacts/logs/{now('EST')}.json"))
file_stream.formatter = JSONFormatter(
	fields = {
		'level' : 'levelname',
		'module' : 'name',
		'function' : 'funcName',
		'process' : 'process',
		'timestamp' : 'asctime',
	}
)

logging.basicConfig(
	level = os.getenv("LOG_LEVEL", "DEBUG").upper(),
	handlers = [
		stdout_stream,
		file_stream
	]
)

# HACK: need to find a better way to track loggers to propagate change in filters, etc.
loggers = []
def Logger(name):
	logger = logging.root.getChild(name)
	loggers.append(logger)
	return logger