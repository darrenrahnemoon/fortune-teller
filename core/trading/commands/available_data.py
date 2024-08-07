import numpy
import pandas
from dataclasses import fields
from argparse import BooleanOptionalAction
from multiprocess import Pool

from core.trading.repository import Repository, SimulationRepository
from core.trading.chart import Chart, CandleStickChart

from core.utils.serializer import RepresentationSerializer
from core.utils.command import CommandSession
from core.trading.chart.command import ChartCommandSessionMixin
from core.utils.collection.command import ListOutputFormatCommandSessionMixin

class AvailableDataCommandSession(
	ChartCommandSessionMixin,
	ListOutputFormatCommandSessionMixin,
	CommandSession
):
	def setup(self):
		super().setup()
		self.add_chart_fields_to_arguments(nargs = '*')
		self.parser.add_argument('repository', type = RepresentationSerializer(Repository).deserialize)
		self.parser.add_argument('--gap-percentage', action = BooleanOptionalAction)
		self.parser.add_argument('--common-timestamps', action = BooleanOptionalAction)
		self.parser.add_argument('--histogram', action = BooleanOptionalAction)
		self.parser.add_argument('--sort-by', type = str)
		self.parser.add_argument('--sort-order', type = str, default = 'ascending')

	def run(self):
		super().run()
		repository: Repository = self.args.repository()
		charts = repository.get_filtered_charts(
			filter = self.get_chart_filter_from_arguments(),
			include_timestamps = True
		)
		charts = list(charts)

		if isinstance(repository, SimulationRepository): 
			for chart in charts:
				chart.count = repository.historical_data[repository.serializers.collection.to_collection_name(chart)].count_documents({})

		if self.args.common_timestamps:
			time_window = repository.get_common_time_window(charts)
			for chart in charts:
				chart.from_timestamp = time_window.from_timestamp
				chart.to_timestamp = time_window.to_timestamp

		if self.args.gap_percentage:
			for chart in charts:
				if not isinstance(chart, CandleStickChart):
					continue
				chart.gap_percentage = repository.get_gap_percentage(chart)

		if self.args.histogram:
			_, edges = numpy.histogram([ chart.from_timestamp.to_pydatetime().timestamp() for chart in charts ], bins = 'auto')
			edges = [ pandas.to_datetime(edge, unit = 's', utc = True) for edge in edges ]
			for index in range(1, len(edges)):
				print(f'\n\n{index}', edges[index - 1], edges[index], sep = '\t')
				for chart in charts:
					if chart.from_timestamp > edges[index - 1] and chart.from_timestamp < edges[index]:
						self.print_chart(chart)
		else:
			if self.args.sort_by:
				charts = sorted(
					charts,
					key = lambda chart: getattr(chart, self.args.sort_by),
					reverse = self.args.sort_order == 'descending'
				)
			for chart in charts:
				self.print_chart(chart)

	def print_chart(self, chart: Chart):
		print(
			*[ getattr(chart, field.name) for field in fields(chart.Query) ],
			chart.from_timestamp,
			chart.to_timestamp,
			chart.count,
			getattr(chart, 'gap_percentage', None),
			sep='\t'
		)