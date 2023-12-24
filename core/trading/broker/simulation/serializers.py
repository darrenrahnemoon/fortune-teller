import pandas
from core.utils.serializer import Serializer

class DataClassMongoDocumentSerializer(Serializer):
	def to_mongo_document(self, value):
		_type = type(value)

		# Exceptional non-primitive data types that pymongo can consume 
		if _type in [ pandas.Timestamp ]:
			return value

		# Data types that we don't have any other options for
		if _type in [ pandas.Timedelta ] or 'Broker' in _type.__name__:
			return repr(value)

		if _type == list:
			return [ self.to_mongo_document(item) for item in value ]

		if _type == dict:
			return { key: self.to_mongo_document(value[key]) for key in value }

		if _type == pandas.Series:
			return self.to_mongo_document([
				dict(timestamp=timestamp, value=value)
				for timestamp, value in value.to_dict().items() 
			])

		if _type == pandas.DataFrame:
			return self.to_mongo_document(value.to_dict('records'))

		if hasattr(value, '__annotations__'):
			result: dict = dict()
			for field_name, field_type in value.__annotations__.items():
				field_value = getattr(value, field_name)
				field_type_name = field_type if type(field_type) == str else field_type.__name__ # For typing.TYPE_CHECKING

				# HACK: for order and position only include their IDs if they're 
				if field_type_name in [ 'Order', 'Position' ] and field_value != None:
					result[field_name] = field_value.id
					continue
				result[field_name] = self.to_mongo_document(field_value)
			return self.to_mongo_document(result)
		return value
