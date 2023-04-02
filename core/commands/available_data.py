import numpy
import pandas
from argparse import BooleanOptionalAction
from multiprocess import Pool

from core.repository import Repository
from core.chart import Chart

from core.utils.serializer import RepresentationSerializer
from core.utils.command import CommandSession
from core.chart.command import ChartCommandSession
from core.utils.collection.command import ListOutputFormatCommandSession

class AvailableDataCommandSession(
	ChartCommandSession,
	ListOutputFormatCommandSession,
	CommandSession
):
	def setup(self):
		super().setup()
		self.add_chart_fields_to_arguments(nargs = '*')
		self.parser.add_argument('repository', type = RepresentationSerializer(Repository).deserialize)
		self.parser.add_argument('--gap-percentage', action = BooleanOptionalAction)
		self.parser.add_argument('--histogram', action = BooleanOptionalAction)

	def run(self):
		super().run()
		repository = self.args.repository()
		charts = repository.get_available_charts(
			filter = self.get_chart_filter_from_arguments(),
			include_timestamps = True
		)
		charts = list(charts)

		if self.args.gap_percentage:
			with Pool(5) as pool:
				interval_charts = [ chart for chart in charts if hasattr(chart, 'interval') ]
				percentages = pool.map(repository.get_gap_percentage, interval_charts)
				for chart, percentage in zip(interval_charts, percentages):
					chart.gap_percentage = percentage

		if self.args.histogram:
			_, edges = numpy.histogram([ chart.from_timestamp.to_pydatetime().timestamp() for chart in charts ], bins = 'auto')
			edges = [ pandas.to_datetime(edge, unit = 's', utc = True) for edge in edges ]
			for index in range(1, len(edges)):
				print(f'\n\n{index}', edges[index - 1], edges[index], sep = '\t')
				for chart in charts:
					if chart.from_timestamp > edges[index - 1] and chart.from_timestamp < edges[index]:
						self.print_chart(chart)
		else:
			for chart in charts:
				self.print_chart(chart)

	def print_chart(self, chart: Chart):
		print(
			type(chart).__name__,
			*[ getattr(chart, key) for key in chart.query_field_names ],
			chart.from_timestamp,
			chart.to_timestamp,
			getattr(chart, 'gap_percentage', None),
			sep='\t'
		)