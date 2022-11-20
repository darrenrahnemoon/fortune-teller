import functools
import os
import sys
import logging
import termcolor

class ColoredMessage(logging.Formatter):
	def __init__(
		self,
		prefix_format = "[%(asctime)s][%(levelname)s %(name)s]:\n",
		message_format = "%(message)s (%(filename)s:%(lineno)d)"
	) -> None:
		self.prefix_format = prefix_format
		self.message_format = message_format

	@functools.cached_property
	def formats(self):
		return {
			logging.DEBUG: termcolor.colored(self.prefix_format, "grey", attrs=[ "bold" ]) + self.message_format,
			logging.INFO: termcolor.colored(self.prefix_format, "cyan") + self.message_format, 
			logging.WARNING: termcolor.colored(self.prefix_format, "yellow") + self.message_format, 
			logging.ERROR: termcolor.colored(self.prefix_format, "red") + self.message_format, 
			logging.CRITICAL: termcolor.colored(self.prefix_format, "red", attrs=[ "bold" ]) + self.message_format, 
		}

	def format(self, record):
		log_format = self.formats.get(record.levelno)
		formatter = logging.Formatter(log_format)
		return formatter.format(record)

def StandardOutput(colored = True):
	handler = logging.StreamHandler(sys.stdout)
	if colored:
		handler.formatter = ColoredMessage()
	return handler

logging.basicConfig(
	level=os.getenv("LOG_LEVEL", "DEBUG"),
	handlers=[StandardOutput(colored=True)]
)