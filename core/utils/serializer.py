from dataclasses import dataclass
from typing import Any
from core.utils.collection import is_any_of
from core.utils.logging import Logger

logger = Logger(__name__)

class Serializer:
	pass

@dataclass
class MappingSerializer(Serializer):
	mapping: dict
	serialize_default: Any = None
	deserialize_default: Any = None

	def serialize(self, value):
		if value == None:
			return None
		return self.mapping.get(value, self.serialize_default)

	def deserialize(self, value):
		if value == None:
			return None
		return next((key for key, value in self.mapping.items() if value == value), self.deserialize_default)

class RepresentationSerializer(Serializer):
	def __init__(
		self,
		from_type: type[object],
		include_subclasses = True
	):
		self.from_type = from_type

		if type(self.from_type) == str:
			logger.debug(f'Cannot infer types from TYPE_CHECKING string. Value will be forwarded without serialization: {self.from_type}')
			return

		self.include_subclasses = include_subclasses
		self.allowed_types = []
		self.append_to_allowed_types(from_type)

		self.context = dict()
		for _type in self.allowed_types:
			self.context[_type.__name__] = _type
			if hasattr(_type, '__annotations__'):
				for field_name, field_type in _type.__annotations__.items():
					if type(field_type) == str:
						logger.debug(f'Cannot infer types for fields that are specifying types in TYPE_CHECKING environments only: {field_name}: {field_type}')
						continue
					try:
						self.context[field_type.__name__] = field_type
					except:
						pass

	def append_to_allowed_types(self, cls):
		self.allowed_types.append(cls)
		if self.include_subclasses:
			for subclass in cls.__subclasses__():
				self.append_to_allowed_types(subclass)

	def serialize(self, value):
		return repr(value)

	def deserialize(self, value: str):
		if value == 'None':
			return None

		if type(self.from_type) == str:
			return value

		if self.from_type == str:
			for string_quote in [ '"', "'" ]:
				if value[0] == string_quote and value[-1] == string_quote:
					value = value[1:-1]
					break
			return value

		if self.from_type in [ bool, int, float ]:
			return self.from_type(value)

		value = value.strip()
		if not is_any_of(self.allowed_types, lambda _type: value.startswith(_type.__name__)):
			raise Exception(f"Invalid representation of '{self.from_type.__name__}' was passed: {value}")
		return eval(value, {}, self.context)
