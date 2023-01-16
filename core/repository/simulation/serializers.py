import pymongo
from pymongo.collection import Collection

from core.chart import Chart, OverriddenChart
from core.interval import * # HACK: only for eval to process intervals # SHOULD DO: find a better way
from core.utils.serializer import Serializer
from core.chart.serializers import ChartDataFrameRecordsSerializer

class ChartMongoFindOptionsSerializer(Serializer):
	def to_find_options(self, overridden_chart: OverriddenChart):
		find_options = {}

		find_options['projection'] = {
			'_id': False,
			Chart.timestamp_field : True,
		}
		for field in overridden_chart.select or []:
			find_options['projection'][field] = True

		find_options['limit'] = overridden_chart.count or 0
		filter = find_options['filter'] = {}
		if overridden_chart.from_timestamp:
			filter.setdefault(Chart.timestamp_field, {})
			filter[Chart.timestamp_field]['$gte'] = overridden_chart.from_timestamp
			find_options['sort'] = [ (Chart.timestamp_field, pymongo.ASCENDING) ]
		if overridden_chart.to_timestamp:
			filter.setdefault(Chart.timestamp_field, {})
			filter[Chart.timestamp_field]['$lte'] = overridden_chart.to_timestamp
			find_options['sort'] = [ (Chart.timestamp_field, pymongo.DESCENDING) ]

		return find_options

class ChartCollectionSerializer(Serializer):
	def to_collection_name(self, overridden_chart: OverriddenChart):
		# If overridden_chart already supplied the name use that
		name = overridden_chart.name
		if name:
			return name

		# Otherwise regenerate the name the same way chart generates it SHOULD DO: DRY out with `chart.name`
		chart_class = overridden_chart.type
		if chart_class:
			return '.'.join([ chart_class.__name__ ] + [ repr(overridden_chart[key]) for key in chart_class.query_fields ])

		raise Exception(f'Unable to deduce collection name from chart params:\n{overridden_chart}')

	def to_chart(self, collection: str or Collection):
		if type(collection) == Collection:
			collection = collection.name
		chunks = collection.split('.')
		chart_class = next(cls for cls in Chart.__subclasses__() if cls.__name__ == chunks[0])
		query_fields = [ eval(chunk) for chunk in chunks[1:] ]
		return chart_class(**dict(zip(chart_class.query_fields, query_fields)))

class SimulationSerializers:
	records = ChartDataFrameRecordsSerializer()
	find_options = ChartMongoFindOptionsSerializer()
	collection = ChartCollectionSerializer()