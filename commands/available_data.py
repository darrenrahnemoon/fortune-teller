import numpy
import pandas
from argparse import ArgumentParser, BooleanOptionalAction, Namespace

from core.repository import Repository
from core.utils.serializer import RepresentationSerializer
from .utils.chart import add_chart_arguments, get_chart_filter

def config(parser: ArgumentParser):
	parser.add_argument('repository', type = RepresentationSerializer(Repository).deserialize)
	parser.add_argument('--gap-percentage', action = BooleanOptionalAction)
	parser.add_argument('--histogram', action = BooleanOptionalAction)
	add_chart_arguments(parser, nargs = '*')

def print_chart(chart):
	print(
		type(chart).__name__,
		*[ getattr(chart, key) for key in chart.query_fields ],
		chart.from_timestamp,
		chart.to_timestamp,
		getattr(chart, 'gap_percentage', None),
		sep='\t'
	)

def handler(args: Namespace):
	repository = args.repository()
	charts = repository.get_available_charts(
		filter = get_chart_filter(args),
		include_timestamps = True
	)
	charts = list(charts)

	if args.gap_percentage:
		for chart in charts:
			chart.gap_percentage = repository.get_gap_percentage(chart)

	if args.histogram:
		_, edges = numpy.histogram([ chart.from_timestamp.to_pydatetime().timestamp() for chart in charts ], bins = 'auto')
		edges = [ pandas.to_datetime(edge, unit = 's', utc = True) for edge in edges ]
		for index in range(1, len(edges)):
			print(f'\n\n{index}: {edges[index - 1]} - {edges[index]}')
			for chart in charts:
				if chart.from_timestamp > edges[index - 1] and chart.from_timestamp < edges[index]:
					print_chart(chart)
	else:
		for chart in charts:
			print_chart(chart)