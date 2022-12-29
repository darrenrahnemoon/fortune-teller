
import pandas
from pymongo.collection import Collection

from core.chart import ChartGroup, Chart
from core.interval import * # HACK: only for eval to process intervals # SHOULD DO: find a better way
from core.utils.serializer import Serializer

class ChartMongoFindOptionsSerializer(Serializer):
	def to_find_options(self, chart: Chart or ChartGroup):
		if isinstance(chart, Chart):
			return self.from_chart_to_find_options(chart)
		elif isinstance(chart, ChartGroup):
			return self.from_chart_group_to_find_options(chart)

	def from_chart_group_to_find_options(self, chart_group: ChartGroup):
		find_options = self.from_chart_to_find_options(chart_group.charts[0])
		find_options['projection'] = { # HACK: currently `select` is not supported for chart_groups
			'_id' : False,
		}
		return find_options

	def from_chart_to_find_options(self, chart: Chart):
		find_options = {}
		find_options['projection'] = [ Chart.timestamp_field ] + chart.select
		filter = find_options['filter'] = {}
		if chart.count:
			find_options['limit'] = chart.count

		if chart.from_timestamp:
			filter[Chart.timestamp_field] = {}
			filter[Chart.timestamp_field]['$gte'] = chart.from_timestamp
		if chart.to_timestamp:
			filter.setdefault(Chart.timestamp_field, {})
			filter[Chart.timestamp_field]['$lte'] = chart.to_timestamp
		return find_options

class ChartCollectionSerializer(Serializer):
	def to_collection_name(self, chart: Chart or ChartGroup):
		if isinstance(chart, Chart):
			return self.from_chart_to_collection_name(chart)
		elif isinstance(chart, ChartGroup):
			return self.from_chart_group_to_collection_name(chart)

	def to_chart(self, collection: str or Collection):
		if type(collection) == Collection:
			collection = collection.name
		chunks = collection.split('.')
		chart_class = next(cls for cls in Chart.__subclasses__() if cls.__name__ == chunks[0])
		query_fields = [ eval(chunk) for chunk in chunks[2:] ]
		return chart_class(**dict(zip(chart_class.query_fields, query_fields)))

	def from_chart_to_collection_name(self, chart: Chart):
		return chart.name

	def from_chart_group_to_collection_name(self, chart_group: ChartGroup):
		return chart_group.name

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
