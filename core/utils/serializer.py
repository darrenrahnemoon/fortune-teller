from core.utils.collection import is_any_of
from core.utils.logging import Logger

logger = Logger(__name__)

class Serializer:
	pass

class MappingSerializer(Serializer):
	def __init__(self, mapping: dict = None) -> None:
		self.mapping = mapping

	def serialize(self, value):
		if value == None:
			return None
		return self.mapping[value]

	def deserialize(self, value):
		if value == None:
			return None
		return next(key for key, value in self.mapping.items() if value == value)

class RepresentationSerializer(Serializer):
	def __init__(self, from_type: type[object], include_subclasses = True):
		self.from_type = from_type

		if type(self.from_type) == str:
			logger.warn(f'Cannot infer types from TYPE_CHECKING string. Value will be forwarded without serialization: {self.from_type}')
			return

		self.include_subclasses = include_subclasses

		self.allowed_types = [ from_type ]
		if self.include_subclasses:
			self.allowed_types.extend(from_type.__subclasses__())

		self.context = dict()
		for _type in self.allowed_types:
			self.context[_type.__name__] = _type
			if hasattr(_type, '__annotations__'):
				for field_name, field_type in _type.__annotations__.items():
					if type(field_type) == str:
						logger.warn(f'Cannot infer types for fields that are specifying types in TYPE_CHECKING environments only: {field_name}: {field_type}')
						continue
					self.context[field_type.__name__] = field_type

	def serialize(self, value):
		return repr(value)

	def deserialize(self, value: str):
		if type(self.from_type) == str:
			return value

		if self.from_type in [ str, bool, int, float ]:
			return self.from_type(value)

		value = value.strip()
		if not is_any_of(self.allowed_types, lambda _type: value.startswith(_type.__name__)):
			raise Exception(f"Invalid representation of '{self.from_type.__name__}'{' or descendants' if self.include_subclasses else ''} was passed: {value}")
		return eval(value, {}, self.context)
