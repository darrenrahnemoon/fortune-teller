import abc
import typing 

Deserialized = typing.TypeVar('Deserialized')
Serialized = typing.TypeVar('Serialized')

class Serializer(typing.Generic[Deserialized, Serialized]):
	@abc.abstractmethod
	def serialize(self, value: Deserialized):
		pass

	@abc.abstractmethod
	def deserialize(self, value: Serialized):
		pass

class MappingSerializer(Serializer[Deserialized, Serialized]):
	def __init__(self, mapping: dict[Deserialized, Serialized] = None) -> None:
		self.mapping = mapping

	def serialize(self, value: Deserialized):
		if value == None:
			return None
		return self.mapping[value]

	def deserialize(self, value: Serialized):
		if value == None:
			return None
		return next(key for key, value in self.mapping.items() if value == value)