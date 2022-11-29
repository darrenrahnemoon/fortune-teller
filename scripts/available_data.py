from core.utils.command import Command
from core.broker import Broker

class AvailableHistoricalDataCommand(Command):
	def config(self):
		self.parser.add_argument('broker', type=Broker.from_repr)

	def handler(self):
		broker: Broker = self.args.broker()
		print(broker.available_data)