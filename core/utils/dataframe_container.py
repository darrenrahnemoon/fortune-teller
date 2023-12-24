import pandas
from dataclasses import dataclass, fields
from abc import abstractproperty
from typing import Any
from core.utils.serializer import RepresentationSerializer

class DataFrameContainerMetaClass(type):
	def __repr__(self):
		return self.__name__

class DataFrameContainer(metaclass = DataFrameContainerMetaClass):

	@dataclass
	class Record:
		pass

	@dataclass
	class Query:
		type: Any = None

	@property
	def name(self):
		return '.'.join([ 
			repr(getattr(self, field.name))
			for field in fields(self.Query)
	])

	@property
	def type(self):
		return type(self)

	@classmethod
	def from_name(cls, name: str):
		chunks = name.split('.')

		chart_class_name = chunks.pop(0)
		chart_class = RepresentationSerializer(cls).deserialize(chart_class_name)
		chart_fields = [ field for field in fields(chart_class.Query) if field.name != 'type' ]
		chart_kwargs = {}

		for field, field_value in zip(chart_fields, chunks):
			chart_kwargs[field.name] = RepresentationSerializer(field.type).deserialize(field_value)

		return chart_class(**chart_kwargs)

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
		record_fields = fields(self.Record)
		if type(value) == pandas.Series and len(record_fields) == 1:
			self.dataframe[self.name, record_fields[0].name] = value
			return

		if type(value) == pandas.DataFrame:
			for column in value.columns:
				self.dataframe[self.name, column] = value[column]