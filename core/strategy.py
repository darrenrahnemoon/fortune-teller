import abc
from dataclasses import dataclass

from core.broker import Broker, SimulationBroker

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
		while not self.is_aborted:
			self.handler()