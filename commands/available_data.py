import pandas

from core.broker import Broker, SimulationBroker
from core.chart import Chart
from core.utils.command import Command, CommandArgumentSerializer

class AvailableHistoricalDataCommand(Command):
	def config(self):
		self.parser.add_argument('--broker', type=CommandArgumentSerializer(Broker).deserialize, default=SimulationBroker())
		self.parser.add_argument('--chart', type=CommandArgumentSerializer(Chart).deserialize)
		for chart_class in [ Chart ] + Chart.__subclasses__():
			self.add_arguments_from_class(chart_class, chart_class.query_fields)

	def handler(self):
		where = {
			key: value 
			for key, value in self.args.__dict__.items() 
			if key != 'broker' and value != None
		}
		charts = self.args.broker.get_available_charts(filter = where, include_timestamps=True)
		for chart in charts:
			print(type(chart).__name__, *[ getattr(chart, key) for key in chart.query_fields ], chart.from_timestamp, chart.to_timestamp, sep='\t')
