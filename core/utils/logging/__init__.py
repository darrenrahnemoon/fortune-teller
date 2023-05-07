import os
import logging
from .handlers import STDOUTHandler


logging.basicConfig(
	level = os.getenv('LOG_LEVEL', 'INFO'),
	handlers = [
		STDOUTHandler(),
	],
)

# HACK: need to find a better way to track loggers to propagate change in filters, etc.
loggers = []
def Logger(name):
	logger = logging.root.getChild(name)
	loggers.append(logger)
	return logger