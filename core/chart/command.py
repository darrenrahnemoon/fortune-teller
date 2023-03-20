from dataclasses import dataclass, field

from core.utils.cls.command import ClassCommandSession
from core.utils.serializer import RepresentationSerializer
from .chart import Chart

@dataclass
class ChartCommandSession(ClassCommandSession):
	chart_fields: set = field(default_factory = set)

	def add_chart_fields_to_arguments(
		self,
		chart_cls: type[Chart] = Chart,
		nargs = None
	):
		group = self.parser.add_argument_group('chart')
		group.add_argument(
			'--chart',
			nargs = '*',
			type = RepresentationSerializer(chart_cls).deserialize
		)
		self.chart_fields.add('chart') # chart is a valid filter

		chart_classes = [ chart_cls ] + chart_cls.__subclasses__()
		for chart_class in chart_classes:
			fields = chart_class.query_fields
			for field in fields:
				self.chart_fields.add(field)

			self.add_class_fields_to_arguments(
				cls = chart_class,
				select = fields,
				kwargs = {
					'nargs' : nargs
				},
				group = group
			)

	def get_chart_filter_from_arguments(self):
		return {
			key: value
			for key, value in self.args.__dict__.items()
			if key in self.chart_fields and value != None
		}
