from commands.chart_filter_command import ChartFilterCommand
class AvailableHistoricalDataCommand(ChartFilterCommand):
	def config(self):
		self.add_chart_arguments(nargs = '*')

	def handler(self):
		repository = self.args.repository()
		charts = repository.get_available_charts(filter = self.get_chart_filter(), include_timestamps = True)
		for chart in charts:
			print(type(chart).__name__, *[ getattr(chart, key) for key in chart.query_fields ], chart.from_timestamp, chart.to_timestamp, sep='\t')
