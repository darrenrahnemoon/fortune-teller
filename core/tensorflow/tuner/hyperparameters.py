from dataclasses import dataclass

@dataclass
class HyperParameterName:
	prefix_delimiter: str = '/'
	name_delimiter: str = '_'
	prefix = []
	def add_prefix(self, *args):
		args = [ str(arg) for arg in args ]
		self.prefix.append(self.name_delimiter.join(args))

	def remove_prefix(self):
		self.prefix.pop()

	def name(self, *args):
		args = [ str(arg) for arg in args ]

		return f'{self.prefix_delimiter.join(self.prefix)}{self.prefix_delimiter}{self.name_delimiter.join(args)}'
