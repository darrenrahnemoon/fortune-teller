import os
import sys
import logging

from .formatter import ColoredFormatter

stdout_stream = logging.StreamHandler(sys.stdout)
stdout_stream.formatter = ColoredFormatter()
logging.basicConfig(
	level = os.getenv("LOG_LEVEL", "DEBUG").upper(),
	handlers = [stdout_stream]
)


# HACK: need to find a better way to track loggers to propagate change in filters, etc.
loggers = []
def Logger(name):
	logger = logging.root.getChild(name)
	loggers.append(logger)
	return logger