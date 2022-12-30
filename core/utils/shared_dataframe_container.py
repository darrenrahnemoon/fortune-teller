import pandas
from abc import abstractproperty
from functools import cached_property
from typing import ClassVar

class SharedDataFrameContainer:
	query_fields: ClassVar[list[str]] = []
	value_fields: ClassVar[list[str]] = []

	@cached_property
	def name(self):
		return '.'.join([ type(self).__name__ ] + [ repr(getattr(self, key)) for key in self.query_fields ])

	def __len__(self) -> int:
		return 0 if type(self.dataframe) == type(None) else len(self.dataframe)

	@abstractproperty
	def dataframe(self):
		pass

	@property
	def data(self) -> pandas.DataFrame:
		return self.dataframe[self.name]

	@data.setter
	def data(self, value: pandas.DataFrame or pandas.Series):
		if type(value) == pandas.Series and len(self.value_fields) == 1:
			self.dataframe[self.name, self.value_fields[0]] = value
			return

		if type(value) == pandas.DataFrame:
			for column in value.columns:
				self.dataframe[self.name, column] = value[column]