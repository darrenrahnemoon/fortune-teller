import logging

# HACK: need to find a better way to track loggers to propagate change in filters, etc.
loggers = []
def Logger(name):
	logger = logging.root.getChild(name)
	loggers.append(logger)
	return logger