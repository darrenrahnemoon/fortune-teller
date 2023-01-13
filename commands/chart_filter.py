import caseconverter
from core.repository import Repository
from core.chart import Chart
from core.utils.command.serializers import CommandArgumentSerializer
from core.utils.command import Command
from core.utils.collection import is_any_of

class ChartFilterCommand(Command):
	def add_chart_arguments(self, nargs = None):
		self.chart_args = set()
		self.parser.add_argument('repository', type = CommandArgumentSerializer(Repository).deserialize)

		self.parser.add_argument(
			'--chart',
			nargs = '*',
			type = CommandArgumentSerializer(Chart).deserialize
		)
		self.chart_args.add('chart') # chart is a valid filter

		for chart_class in [ Chart ] + Chart.__subclasses__():
			for field in chart_class.query_fields:
				self.chart_args.add(field)

			self.add_arguments_from_class(
				cls = chart_class,
				select = chart_class.query_fields,
				kwargs = {
					'nargs' : nargs
				}
			)

	def handler(self):
		return super().handler()

	def get_chart_filter(self):
		return {
			key: value
			for key, value in self.args.__dict__.items()
			if key in self.chart_args and value != None
		}

	def add_arguments_from_class(
		self,
		cls: type,
		select = [],
		kwargs = {}
	):
		select = select if len(select) else cls.__annotations__.keys()
		for field_name in select:
			option_string = f'--{caseconverter.kebabcase(field_name)}'

			# skip if option string has been previously defined
			if is_any_of(self.parser._actions, lambda action: option_string in action.option_strings):
				continue

			field_type = cls.__annotations__[field_name]
			self.parser.add_argument(option_string, type = CommandArgumentSerializer(field_type).deserialize, **kwargs)
