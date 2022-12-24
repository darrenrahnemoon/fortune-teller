import pymongo
import logging
from dataclasses import dataclass

from core.broker.simulation.report import BacktestReport
from core.chart.serializers import ChartDataFrameRecordsSerializer
from core.broker.simulation.serializers import (
	ChartCollectionSerializer,
	ChartMongoFindOptionsSerializer,
	DataClassMongoDocumentSerializer
)
from core.broker.broker import ChartCombinations
from core.chart import Chart
from core.interval import * # HACK: used for eval to reverse __repr__

from core.utils.mongo import MongoRepository
from core.utils.time import normalize_timestamp

logger = logging.getLogger(__name__)

@dataclass
class SimulationRepository(MongoRepository):
	dataframe_records_serializer = ChartDataFrameRecordsSerializer()
	mongo_find_options_serializer = ChartMongoFindOptionsSerializer()
	dataclass_mongo_document_serializer = DataClassMongoDocumentSerializer()
	chart_collection_serializer = ChartCollectionSerializer()

	def read_chart_raw(self, chart: Chart) -> list:
		collection = self.historical_data[self.chart_collection_serializer.to_collection_name(chart)]
		return list(collection.find(**self.mongo_find_options_serializer.to_find_options(chart)))

	def read_chart(self, chart: Chart) -> pandas.DataFrame:
		records = self.read_chart_raw(chart)
		return self.dataframe_records_serializer.to_dataframe(records, chart)

	def write_chart(self, chart: Chart):
		data = chart.data
		if len(data) == 0:
			logger.warn(f'Attempted to write an empty {chart} into database. Skipping...')
			return

		collection = self.ensure_collection_for_chart(chart)
		rows = self.dataframe_records_serializer.to_records(data)
		self.upsert(collection, rows)

	def ensure_collection_for_chart(self, chart: Chart):
		collection = self.historical_data[self.chart_collection_serializer.to_collection_name(chart)]

		if Chart.timestamp_field not in collection.index_information():
			collection.create_index([(Chart.timestamp_field, pymongo.ASCENDING)], name=Chart.timestamp_field, unique=True)

		return collection

	def drop_collection_for_chart(self, chart: Chart):
		self.historical_data[self.chart_collection_serializer.to_collection_name(chart)].drop()

	def get_available_chart_combinations(self) -> ChartCombinations: 
		collection_names = self.historical_data.list_collection_names()
		collection_names.sort()
		available_data = dict()
		for name in collection_names:
			chart = self.chart_collection_serializer.to_chart(name)
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

	def get_available_charts(self, filter = {}, include_timestamps = False) -> list[Chart]:
		collection_names = self.historical_data.list_collection_names()
		collection_names.sort()
		charts = []
		for name in collection_names:
			chart = self.chart_collection_serializer.to_chart(name)
			if not filter.items() <= chart.__dict__.items():
				continue
			if include_timestamps:
				chart.from_timestamp = self.get_min_available_timestamp_for_chart(chart)
				chart.to_timestamp = self.get_max_available_timestamp_for_chart(chart)
			charts.append(chart)
		return charts

	def get_max_available_timestamp_for_chart(self, chart: Chart):
		collection = self.historical_data[self.chart_collection_serializer.to_collection_name(chart)]
		record = collection.find_one(sort=[(Chart.timestamp_field, pymongo.DESCENDING)])
		return normalize_timestamp(record[Chart.timestamp_field]) if record else None

	def get_min_available_timestamp_for_chart(self, chart: Chart):
		collection = self.historical_data[self.chart_collection_serializer.to_collection_name(chart)]
		record = collection.find_one(sort=[(Chart.timestamp_field, pymongo.ASCENDING)])
		return normalize_timestamp(record[Chart.timestamp_field]) if record else None

	def write_backtest_report(self, report: BacktestReport):
		collection = self.backtest_reports.get_collection(type(report.strategy).__name__)
		serialized_report = self.dataclass_mongo_document_serializer.to_mongo_document(report)
		collection.insert_one(serialized_report)

	@property
	def historical_data(self):
		return self.client['trading']

	@property
	def backtest_reports(self):
		return self.client['trading_backtest_reports']