import pymongo
from pymongo.collection import Collection

from core.trading.chart import Chart, OverriddenChart
from core.trading.interval import * # HACK: only for eval to process intervals # SHOULD DO: find a better way
from core.utils.serializer import Serializer
from core.trading.chart.serializers import ChartRecordsSerializer

class ChartMongoFindOptionsSerializer(Serializer):
	def to_find_options(self, chart: OverriddenChart):
		find_options = {}

		# Only select the fields needed
		find_options['projection'] = {
			'_id': False,
			'timestamp' : True,
		}
		for field in chart.select:
			find_options['projection'][field] = True

		find_options['limit'] = chart.count or 0
		filter = find_options['filter'] = {}

		if chart.from_timestamp:
			filter.setdefault('timestamp', {})
			filter['timestamp']['$gte'] = chart.from_timestamp
			find_options['sort'] = [ ('timestamp', pymongo.ASCENDING) ]

		if chart.to_timestamp:
			filter.setdefault('timestamp', {})
			filter['timestamp']['$lte'] = chart.to_timestamp
			if chart.count:
				find_options['sort'] = [ ('timestamp', pymongo.DESCENDING) ]

		return find_options

class ChartCollectionSerializer(Serializer):
	def to_collection_name(self, chart: OverriddenChart):
		if chart.name:
			return chart.name

		raise Exception(f'Unable to deduce collection name from chart params:\n{chart}')

	def to_chart(self, collection: str or Collection):
		if type(collection) == Collection:
			collection = collection.name
		return Chart.from_name(collection)

class SimulationSerializers:
	records = ChartRecordsSerializer()
	find_options = ChartMongoFindOptionsSerializer()
	collection = ChartCollectionSerializer()