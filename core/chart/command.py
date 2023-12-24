from dataclasses import dataclass, field, fields

from core.utils.cls.command import ClassCommandSession
from core.utils.serializer import RepresentationSerializer
from .chart import Chart

@dataclass
class ChartCommandSessionMixin(ClassCommandSession):
	chart_fields: set = field(default_factory = set)

	def add_chart_fields_to_arguments(
		self,
		chart_cls: type[Chart] = Chart,
		nargs = None,
	):
		is_multiple_arguments = nargs in [ '*', '+' ]
		group = self.parser.add_argument_group('chart')
		group.add_argument(
			'--type',
			nargs = nargs,
			type = RepresentationSerializer(chart_cls).deserialize,
			default = [] if is_multiple_arguments else None
		)
		self.chart_fields.add('type') # chart is a valid filter

		chart_classes = [ chart_cls ] + chart_cls.__subclasses__()
		for chart_class in chart_classes:
			field_names = [ field.name for field in fields(chart_class) ]
			for field_name in field_names:
				self.chart_fields.add(field_name)

			self.add_class_fields_to_arguments(
				cls = chart_class,
				select = field_names,
				kwargs = {
					'nargs' : nargs,
					'default': [] if is_multiple_arguments else None,
				},
				group = group
			)

	def get_chart_filter_from_arguments(self) -> dict[str, list]:
		return {
			key: value
			for key, value in self.args.__dict__.items()
			if key in self.chart_fields \
			and value != None \
			and (type(value) == list and not len(value) == 0) # for nargs = '*'
		}
