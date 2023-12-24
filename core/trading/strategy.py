import abc
from dataclasses import dataclass
from core.utils.logging import Logger

logger = Logger(__name__)

@dataclass
class Strategy:
	def __post_init__(self):
		self.is_aborted = False

	def cleanup(self):
		pass

	@abc.abstractmethod
	def handler(self):
		pass

	def abort(self):
		self.is_aborted = True
		self.cleanup()

	def run(self):
		logger.info(f'Started running {type(self).__name__}.')
		while not self.is_aborted:
			self.handler()
		logger.info(f'Stopped running {type(self).__name__}.')