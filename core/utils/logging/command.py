from dataclasses import dataclass
from core.utils.logging import logging, loggers
from core.utils.logging.handlers import JSONFileHandler, STDOUTHandler
from core.utils.logging.filter import MessageFilter
from core.utils.serializer import MappingSerializer

@dataclass
class LoggingCommandSession:
	logging_handlers = MappingSerializer({
		'file' : JSONFileHandler,
		'stdout' : STDOUTHandler,
	})

	def setup(self):
		super().setup()

		logging_argument_group = self.parser.add_argument_group('logging')
		logging_argument_group.add_argument(
			'--log-level',
			choices = [ 'CRITICAL', 'FATAL', 'ERROR', 'WARNING', 'WARN', 'INFO', 'DEBUG' ]
		)
		logging_argument_group.add_argument(
			'--log-filter',
			nargs = '+',
			type = str,
			default = []
		)
		logging_argument_group.add_argument(
			'--log-destinations',
			nargs = '+',
			type = str,
			choices = list(self.logging_handlers.mapping.keys()),
			default = list(self.logging_handlers.mapping.keys())
		)

	def run(self):
		super().run()

		logging.basicConfig(
			level = self.args.log_level,
			handlers = [
				self.logging_handlers.serialize(handler)()
				for handler in self.args.log_destinations
			],
		)

		if len(self.args.log_filter):
			log_filter = MessageFilter(self.args.log_filter)
			logging.root.addFilter(log_filter)
			for logger in loggers:
				logger.addFilter(log_filter)
