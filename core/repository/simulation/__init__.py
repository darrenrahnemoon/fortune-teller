import logging
from typing import Iterable
import pandas
from dataclasses import dataclass
import pymongo

from pymongo.database import Database

from .serializers import SimulationSerializers
from core.chart import Chart, ChartGroup, ChartParams
from core.repository.repository import ChartCombinations, Repository
from core.utils.time import TimeWindow, normalize_timestamp
from core.utils.mongo import MongoRepository

logger = logging.getLogger(__name__)

@dataclass
class SimulationRepository(Repository, MongoRepository):
	serializers = SimulationSerializers()

	def read_chart(
		self,
		chart: Chart = None,
		database: Database = None,
		**overrides
	) -> pandas.DataFrame:
		database = database or self.historical_data
		chart_params = ChartParams(chart, overrides)
		find_options = self.serializers.find_options.to_find_options(chart_params)

		collection = self.serializers.collection.to_collection_name(chart_params)
		collection = database.get_collection(collection)
		records = collection.find(**find_options)

		dataframe = self.serializers.records.to_dataframe(
			records,
			name = chart_params['name'],
			select = chart_params['select']
		)

		logger.debug(f'Read chart:\n{dataframe}')
		return dataframe

	def write_chart(
		self,
		chart: Chart or ChartGroup = None,
		database: Database = None,
		**overrides
	):
		database = database or self.historical_data
		chart_params = ChartParams(chart, overrides)
		data = chart_params['data']
		if len(data) == 0:
			logger.warn(f"Attempted to write an empty {chart_params['name']} into database. Skipping...")
			return

		logger.debug(f'Writing chart:\n{data}')
		collection = self.serializers.collection.to_collection_name(chart_params)
		collection = self.ensure_time_series_collection(
			database = database,
			name = collection
		)
		records = self.serializers.records.to_records(data)
		self.upsert(
			collection = collection,
			records = records
		)

	def remove_historical_data(
		self,
		chart: Chart = None,
		**overrides
	):
		chart_params = ChartParams(chart, overrides)
		collection = self.serializers.collection.to_collection_name(chart_params)
		self.historical_data.drop_collection(collection)

	@classmethod
	def get_common_time_window(
		self,
		chart_group: ChartGroup = None,
		**overrides
	) -> TimeWindow:
		chart_params = ChartParams(chart_group, overrides)
		from_timestamp = []
		to_timestamp = []
		for chart in chart_params['charts']:
			from_timestamp.append(self.get_min_available_timestamp_for_chart(chart))
			to_timestamp.append(self.get_max_available_timestamp_for_chart(chart))

		return TimeWindow(
			from_timestamp = max(from_timestamp),
			to_timestamp = min(to_timestamp)
		)

	def get_available_chart_combinations(self) -> ChartCombinations:
		# SHOULD DO: clean this up or remove entirely
		collection_names = self.historical_data.list_collection_names()
		collection_names.sort()
		available_data = dict()
		for name in collection_names:
			chart = self.serializers.collection.to_chart(name)
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

	def get_available_charts(
		self,
		filter = {},
		include_timestamps = False
	) -> Iterable[Chart]:
		collection_names = self.historical_data.list_collection_names()
		collection_names.sort()
		for name in collection_names:
			chart = self.serializers.collection.to_chart(name)
			if not filter.items() <= chart.__dict__.items():
				continue
			if include_timestamps:
				chart.from_timestamp = self.get_min_available_timestamp_for_chart(chart)
				chart.to_timestamp = self.get_max_available_timestamp_for_chart(chart)
			yield chart

	def get_max_available_timestamp_for_chart(
		self,
		chart: Chart = None,
		**overrides
	) -> pandas.Timestamp:
		chart_params = ChartParams(chart, overrides)
		collection = self.historical_data[self.serializers.collection.to_collection_name(chart_params)]
		record = collection.find_one(sort = [ (Chart.timestamp_field, pymongo.DESCENDING) ])
		return normalize_timestamp(record[Chart.timestamp_field]) if record else None

	def get_min_available_timestamp_for_chart(
		self,
		chart: Chart = None,
		**overrides
	) -> pandas.Timestamp:
		chart_params = ChartParams(chart, overrides)
		collection = self.historical_data[self.serializers.collection.to_collection_name(chart_params)]
		record = collection.find_one(sort = [ (Chart.timestamp_field, pymongo.ASCENDING) ])
		return normalize_timestamp(record[Chart.timestamp_field]) if record else None

	@property
	def historical_data(self):
		return self.client['historical_data']
