import sys
from dataclasses import dataclass
from dataclass_csv import DataclassWriter
from core.utils.cls.repr import pretty_repr

@dataclass
class ListOutputFormatCommandSession:
	def setup(self):
		super().setup()
		self.parser.add_argument('--output-format', choices = [ 'csv', 'repr', 'pretty_repr' ], default = 'raw')

	def print_list(self, data: list, cls):
		if self.args.output_format == 'csv':
			DataclassWriter(sys.stdout, data, cls)
		elif self.args.output_format == 'repr':
			print(data)
		elif self.args.output_format == 'pretty_repr':
			print(pretty_repr(data))