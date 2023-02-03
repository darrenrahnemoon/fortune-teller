from argparse import ArgumentParser, Namespace
from core.chart import Chart
from core.utils.serializer import RepresentationSerializer
import core.utils.command.cls

def add_args(
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

		core.utils.command.cls.add_fields_to_args(
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

def get_filter_from_args(args: Namespace):
	return {
		key: value
		for key, value in args.__dict__.items()
		if key in args.chart_fields and value != None
	}
