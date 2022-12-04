import os
import sys
import pandas
import pymongo
import logging
from pymongo.collection import Collection
from dataclasses import dataclass, field

from core.broker.simulation.report import BacktestReport
from core.broker.simulation.serializers import (
	ChartCollectionSerializer,
	ChartDataFrameSerializer,
	ChartFilterSerializer,
	DataClassMongoSerializer
)
from core.broker.broker import ChartCombinations
from core.chart import Chart
from core.interval import * # HACK: used for eval to reverse __repr__

from core.utils.time import normalize_timestamp

logger = logging.getLogger(__name__)

chart_dataframe_serializer = ChartDataFrameSerializer()
chart_filter_serializer = ChartFilterSerializer()
dataclass_mongo_serializer = DataClassMongoSerializer()

@dataclass
class Repository:
	client: pymongo.MongoClient = field(default_factory=lambda: pymongo.MongoClient(os.getenv('DB_URI'), tz_aware=True))

	def __post_init__(self):
		self.chart_collection_serializer = ChartCollectionSerializer(self.client['trading'])

	def read_chart(self, chart: Chart, limit = 0, inplace = False):
		collection = self.chart_collection_serializer.serialize(chart)
		filter = chart_filter_serializer.serialize(chart)
		records = list(collection.find(filter, limit=limit))
		if inplace:
			chart.dataframe = chart_dataframe_serializer.deserialize(records, chart)
		return records

	def write_chart(self, chart: Chart):
		data = chart.data
		if len(data) == 0:
			logger.warn(f'Attempted to write an empty {chart} into database. Skipping...')
			return

		collection = self.ensure_collection_for_chart(chart)
		rows = chart_dataframe_serializer.serialize(data)
		self.upsert(collection, rows)

	def upsert(self, collection: Collection, rows: list):
		try:
			collection.insert_many(rows)
		except:
			index = sys.exc_info()[1].details['writeErrors'][0]['index']
			failed_row = rows[index]
			del failed_row['_id'] # Cannot upsert a new generated `_id` on existing document

			logger.debug(f'Duplicated row found. Upserting...\n{failed_row}')
			collection.update_one({ 'timestamp': failed_row['timestamp'] }, { '$set' : failed_row })

			start_from = index + 1
			if start_from == len(rows):
				return
			self.upsert(collection, rows[start_from:])

	def ensure_collection_for_chart(self, chart: Chart):
		collection = self.chart_collection_serializer.serialize(chart)
		index_information = collection.index_information()
		if 'timestamp' not in index_information:
			collection.create_index([('timestamp', pymongo.ASCENDING)], name='timestamp', unique=True)
		return collection

	def drop_collection_for_chart(self, chart: Chart):
		self.chart_collection_serializer.serialize(chart).drop()

	def get_available_chart_combinations(self) -> ChartCombinations: 
		collection_names = self.client['trading'].list_collection_names().sort()
		available_data = dict()
		for name in collection_names:
			chart = self.get_chart_from_collection_name(name)
			combinations = available_data.setdefault(type(chart), [])
			symbol_combinations = next((combination for combination in combinations if chart.symbol in combination['symbol'] ), None)
			if symbol_combinations == None:
				symbol_combinations = { 'symbol' : [ chart.symbol ] }
			for field_key in chart.query_fields:
				if field_key == 'symbol':
					continue
				field_value = getattr(chart, field_key)
				field_combinations = symbol_combinations.setdefault(field_key, [])
				if field_value not in field_combinations:
					field_combinations.append(field_value)
			return available_data

	def get_available_charts(self, include_timestamps = False) -> list[Chart]:
		collection_names = self.client['trading'].list_collection_names().sort()
		def to_chart(name: str):
			chart = chart_dataframe_serializer.deserialize(name)
			if include_timestamps:
				chart.from_timestamp = self.get_min_available_timestamp_for_chart(chart)
				chart.to_timestamp = self.get_max_available_timestamp_for_chart(chart)
			return chart
		return [ to_chart(name) for name in collection_names ]

	def get_max_available_timestamp_for_chart(self, chart: Chart):
		collection = self.chart_collection_serializer.serialize(chart)
		record = collection.find_one(sort=[('timestamp', pymongo.DESCENDING)])
		return normalize_timestamp(record['timestamp']) if record else None

	def get_min_available_timestamp_for_chart(self, chart: Chart):
		collection = self.chart_collection_serializer.serialize(chart)
		record = collection.find_one(sort=[('timestamp', pymongo.ASCENDING)])
		return normalize_timestamp(record['timestamp']) if record else None

	def write_backtest_report(self, report: BacktestReport):
		collection = self.client['trading_backtest_reports'][type(report.strategy).__name__]
		serialized_report = dataclass_mongo_serializer.serialize(report)
		collection.insert_one(serialized_report)
