import pandas
from dataclasses import fields
from abc import abstractproperty
from typing import ClassVar
from core.utils.serializer import RepresentationSerializer

class DataFrameContainerMetaClass(type):
	def __repr__(self):
		return self.__name__

class DataFrameContainer(metaclass = DataFrameContainerMetaClass):
	query_field_names: ClassVar[list[str]] = [ 'type' ]
	value_field_names: ClassVar[list[str]] = []

	@property
	def name(self):
		return '.'.join([ repr(getattr(self, key)) for key in self.query_field_names ])

	@property
	def type(self):
		return type(self)

	@classmethod
	def from_name(cls, name: str):
		chunks = name.split('.')

		chart_class_name = chunks[0]
		chart_class = RepresentationSerializer(cls).deserialize(chart_class_name)
		chart_class_fields = fields(chart_class)
		chart_kwargs = {}

		for field_name, field_value in zip(chart_class.query_field_names, chunks):
			field = next((field for field in chart_class_fields if field.name == field_name), None)
			if not field:
				continue

			chart_kwargs[field_name] = RepresentationSerializer(field.type).deserialize(field_value)

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
		if type(value) == pandas.Series and len(self.value_field_names) == 1:
			self.dataframe[self.name, self.value_field_names[0]] = value
			return

		if type(value) == pandas.DataFrame:
			for column in value.columns:
				self.dataframe[self.name, column] = value[column]