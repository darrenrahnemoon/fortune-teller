import typing

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