
import pandas
from pymongo.database import Database
from pymongo.collection import Collection
from dataclasses import dataclass

from core.interval import * # HACK: only for eval to process intervals # SHOULD DO: find a better way
from core.chart.chart import Chart
from core.utils.serializer import Serializer

class ChartDataFrameSerializer(Serializer[pandas.DataFrame or pandas.Series, list[dict]]):
	def serialize(self, dataframe):
		if type(dataframe) == pandas.DataFrame:
			rows = dataframe.reset_index().to_dict(orient='records')
		elif type(dataframe) == pandas.Series:
			rows = [
				dict(timestamp=timestamp, value=value)
				for timestamp, value in dataframe.to_dict().items() 
			]
		else:
			raise Exception(f'Invalid data passed to `ChartDataFrameSerializer`: {dataframe}')

		seen = set()
		return [
			row for row in rows 
			if not (
				row['timestamp'] in seen 
				or seen.add(row['timestamp'])
			)
		]

	def deserialize(self, records, chart: Chart):
		return pandas.DataFrame.from_records(records, columns=[ 'timestamp' ] + chart.value_fields)

class ChartFilterSerializer(Serializer[Chart, dict]):
	def serialize(self, chart: Chart):
		filter = { 'timestamp' : {} }
		if chart.from_timestamp:
			filter['timestamp']['$gte'] = chart.from_timestamp
		if chart.to_timestamp:
			filter['timestamp']['$lte'] = chart.to_timestamp
		return filter

@dataclass(init=True, repr=False, eq=False, order=False, unsafe_hash=False, frozen=False, match_args=False, kw_only=False, slots=False)
class ChartCollectionSerializer(Serializer[Chart, str or Collection]):
	database: Database

	def serialize(self, chart: Chart):
		collection = f"{type(chart).__name__}.{'.'.join([ str(getattr(chart, key)) for key in chart.query_fields ])}"
		return self.database[collection]

	def deserialize(self, collection: str or Collection):
		if type(collection) == Collection:
			collection = collection.name
		chunks = collection.split('.')
		chart_class = next(cls for cls in Chart.__subclasses__() if cls.__name__ == chunks[0])
		query_fields = [ chunks[1] ] # HACK: symbol wasn't converted to a repr instead it was converted to string so it cannot be evaluated
		query_fields = query_fields + [ eval(chunk) for chunk in chunks[2:] ]
		return chart_class(**dict(zip(chart_class.query_fields, query_fields)))

class DataClassMongoSerializer(Serializer[typing.Any, dict]):
	def serialize(self, value):
		_type = type(value)

		# Exceptional non-primitive data types that pymongo can consume 
		if _type in [ pandas.Timestamp ]:
			return value

		# Data types that we don't have any other options for
		if _type in [ pandas.Timedelta ] or 'Broker' in _type.__name__:
			return repr(value)

		if _type == list:
			return [ self.serialize(item) for item in value ]

		if _type == dict:
			return { key: self.serialize(value[key]) for key in value }

		if _type == pandas.Series:
			return self.serialize([
				dict(timestamp=timestamp, value=value)
				for timestamp, value in value.to_dict().items() 
			])

		if _type == pandas.DataFrame:
			return self.serialize(value.to_dict('records'))

		if hasattr(value, '__annotations__'):
			result: dict = dict()
			for field_name, field_type in value.__annotations__.items():
				field_value = getattr(value, field_name)
				field_type_name = field_type if type(field_type) == str else field_type.__name__
				if field_type_name in [ 'Order', 'Position' ] and field_value != None:
					result[field_name] = field_value.id
					continue
				result[field_name] = self.serialize(field_value)
			return self.serialize(result)
		return value
