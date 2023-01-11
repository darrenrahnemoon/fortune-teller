import pandas

from core.repository import Repository, SimulationRepository
from core.chart import Chart
from core.utils.command import Command, CommandArgumentSerializer

class AvailableHistoricalDataCommand(Command):
	def config(self):
		self.parser.add_argument('--repository', type = CommandArgumentSerializer(Repository).deserialize, default = SimulationRepository())
		self.parser.add_argument('--chart', nargs = "*", type = CommandArgumentSerializer(Chart).deserialize)
		for chart_class in [ Chart ] + Chart.__subclasses__():
			self.add_arguments_from_class(
				cls = chart_class,
				select = chart_class.query_fields,
				kwargs = {
					'nargs' : '*'
				}
			)

	def handler(self):
		repository = self.args.repository()
		where = {
			key: value 
			for key, value in self.args.__dict__.items() 
			if key != 'repository' and value != None
		}
		charts = repository.get_available_charts(filter = where, include_timestamps = True)
		for chart in charts:
			print(type(chart).__name__, *[ getattr(chart, key) for key in chart.query_fields ], chart.from_timestamp, chart.to_timestamp, sep='\t')
