from argparse import ArgumentParser, BooleanOptionalAction, Namespace

from core.repository import Repository
from core.utils.serializer import RepresentationSerializer
from .utils.chart import add_chart_arguments, get_chart_filter

def config(parser: ArgumentParser):
	parser.add_argument('repository', type = RepresentationSerializer(Repository).deserialize)
	parser.add_argument('--timestamps', action = BooleanOptionalAction)
	parser.add_argument('--gap-percentage', action = BooleanOptionalAction)
	add_chart_arguments(parser, nargs = '*')

def handler(args: Namespace):
	repository = args.repository()
	charts = repository.get_available_charts(
		filter = get_chart_filter(args),
		include_timestamps = args.timestamps or args.gap_percentage
	)
	for chart in charts:
		gap_percentage = repository.get_gap_percentage(chart) if args.gap_percentage and hasattr(chart, 'interval') else None

		print(
			type(chart).__name__,
			*[ getattr(chart, key) for key in chart.query_fields ],
			chart.from_timestamp,
			chart.to_timestamp,
			f'{gap_percentage * 100}%',
			sep='\t'
		)
