from argparse import ArgumentParser, Namespace
from .cls import add_class_fields_as_arguments
from core.chart import Chart
from core.utils.serializer import RepresentationSerializer

def add_chart_arguments(
	parser: ArgumentParser,
	chart_cls: type[Chart] = Chart,
	nargs = None
):
	chart_fields = set()
	parser.add_argument(
		'--chart',
		nargs = '*',
		type = RepresentationSerializer(chart_cls).deserialize
	)
	chart_fields.add('chart') # chart is a valid filter

	chart_classes = [ chart_cls ] + chart_cls.__subclasses__()
	for chart_class in chart_classes:
		fields = chart_class.query_fields
		for field in fields:
			chart_fields.add(field)

		add_class_fields_as_arguments(
			cls = chart_class,
			parser = parser,
			select = fields,
			kwargs = {
				'nargs' : nargs
			}
		)
	parser.set_defaults(
		chart_fields = chart_fields
	)

def get_chart_filter(args: Namespace):
	return {
		key: value
		for key, value in args.__dict__.items()
		if key in args.chart_fields and value != None
	}