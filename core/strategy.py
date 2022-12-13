import abc
from dataclasses import dataclass

from core.broker import Broker, SimulationBroker

@dataclass
class Strategy:
	def __post_init__(self):
		self.is_aborted = False
		self.setup()

	def setup(self):
		pass

	def cleanup(self):
		pass

	@abc.abstractmethod
	def handler(self):
		pass

	def abort(self):
		self.is_aborted = True
		self.cleanup()

	def backtest(self, broker: SimulationBroker = None, **kwargs):
		broker = broker or SimulationBroker(**kwargs)
		for field_name, field_type in type(self).__annotations__.items():
			if issubclass(field_type, Broker) or 'Broker' in str(field_type):
				setattr(self, field_name, broker)
		broker.backtest(self)

	def run(self):
		while not self.is_aborted:
			self.handler()