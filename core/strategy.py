import abc
import forge

from dataclasses import dataclass

from core.broker import Broker, SimulationBroker

@dataclass
class Strategy:
	broker: 'Broker' = None
	is_aborted: bool = False

	def __post_init__(self):
		self.setup()

	def setup(self):
		pass

	def cleanup(self):
		pass

	@abc.abstractmethod
	def handler(self):
		pass

	def abort(self):
		self.cleanup()
		raise Exception(f'{self} aborted.')

	def run(self):
		if type(self.broker) == SimulationBroker:
			self.broker.backtest(self)
		else:
			while True:
				self.handler()