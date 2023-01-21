from argparse import ArgumentParser, Namespace

from core.repository import Repository
from core.utils.serializer import RepresentationSerializer
from .utils.chart import add_chart_arguments, get_chart_filter

def config(parser: ArgumentParser):
	parser.add_argument('repository', type = RepresentationSerializer(Repository).deserialize)
	add_chart_arguments(parser, nargs = '*')

def handler(args: Namespace):
	repository = args.repository()
	charts = repository.get_available_charts(
		filter = get_chart_filter(args),
		include_timestamps = True
	)
	for chart in charts:
		print(
			type(chart).__name__,
			*[ getattr(chart, key) for key in chart.query_fields ],
			chart.from_timestamp,
			chart.to_timestamp,
			sep='\t'
		)
