import logging
import functools
import termcolor

class ColoredFormatter(logging.Formatter):
	def __init__(
		self,
		colored_format = '',
		uncolored_format = '',
	) -> None:
		self.colored_format = colored_format
		self.uncolored_format = uncolored_format

	@functools.cached_property
	def formatters(self):
		return {
			logging.DEBUG: logging.Formatter(
				termcolor.colored(self.colored_format, "grey", attrs=[ "bold" ]) + self.uncolored_format
			),
			logging.INFO: logging.Formatter(
				termcolor.colored(self.colored_format, "cyan") + self.uncolored_format
			),
			logging.WARNING: logging.Formatter(
				termcolor.colored(self.colored_format, "yellow") + self.uncolored_format
			),
			logging.ERROR: logging.Formatter(
				termcolor.colored(self.colored_format, "red") + self.uncolored_format
			),
			logging.CRITICAL: logging.Formatter(
				termcolor.colored(self.colored_format, "red", attrs=[ "bold" ]) + self.uncolored_format
			),
		}

	def format(self, record):
		return self.formatters[record.levelno].format(record)
