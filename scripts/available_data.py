from core.broker import Broker
from core.utils.command import Command

class AvailableHistoricalDataCommand(Command):
	def config(self):
		self.parser.add_argument('broker', type=Broker.from_repr)
		self.parser.add_argument('--orient', type=str)

	def handler(self):
		broker: Broker = self.args.broker()
		available_data = broker.get_available_charts(self.args.orient or 'combinations')
		if type(available_data) == list:
			for chart in available_data:
				print(chart)
		else:
			print(available_data)