import pandas
import pymongo
from multiprocess import Pool
from typing import Iterable
from dataclasses import dataclass

from .serializers import SimulationSerializers
from core.chart import Chart, ChartGroup, ChartParams
from core.repository.repository import ChartCombinations, Repository
from core.utils.time import TimeWindow, normalize_timestamp, now
from core.utils.mongo import MongoRepository
from core.utils.logging import logging
from core.utils.cls import pretty_repr

logger = logging.getLogger(__name__)

@dataclass
class SimulationRepository(Repository, MongoRepository):
	serializers = SimulationSerializers()

	def read_chart(
		self,
		chart: Chart or ChartParams = None,
		collection: str = None,
		database: str = None,
		**overrides
	) -> pandas.DataFrame:
		database = self.client[database] if database else self.historical_data
		chart_params = ChartParams(chart, overrides)
		find_options = self.serializers.find_options.to_find_options(chart_params)

		collection = collection or self.serializers.collection.to_collection_name(chart_params)
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
		chart: Chart or ChartGroup or ChartParams = None,
		collection: str = None,
		database: str = None,
		**overrides
	):
		chart_params = ChartParams(chart, overrides)
		database = self.client[database] if database else self.historical_data
		data = chart_params['data']
		if len(data) == 0:
			logger.warn(f"Attempted to write an empty {chart_params['name']} into database. Skipping...")
			return

		logger.debug(f'Writing chart:\n{data}')
		collection = collection or self.serializers.collection.to_collection_name(chart_params)
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
		chart: Chart or ChartParams = None,
		**overrides
	):
		chart_params = ChartParams(chart, overrides)
		collection = self.serializers.collection.to_collection_name(chart_params)
		self.historical_data.drop_collection(collection)

	@classmethod
	def get_common_time_window(
		self,
		chart_group: ChartGroup or ChartParams = None,
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

			should_skip = False
			for key, value in chart.__dict__.items():
				if (key in filter) and (value not in filter[key]):
					should_skip = True
			if should_skip:
				continue

			if include_timestamps:
				chart.from_timestamp = self.get_min_available_timestamp_for_chart(chart)
				chart.to_timestamp = self.get_max_available_timestamp_for_chart(chart)
			yield chart

	def get_max_available_timestamp_for_chart(
		self,
		chart: Chart or ChartParams = None,
		**overrides
	) -> pandas.Timestamp:
		chart_params = ChartParams(chart, overrides)
		collection = self.historical_data[self.serializers.collection.to_collection_name(chart_params)]
		record = collection.find_one(sort = [ (Chart.timestamp_field, pymongo.DESCENDING) ])
		return normalize_timestamp(record[Chart.timestamp_field]) if record else None

	def get_min_available_timestamp_for_chart(
		self,
		chart: Chart or ChartParams = None,
		**overrides
	) -> pandas.Timestamp:
		chart_params = ChartParams(chart, overrides)
		collection = self.historical_data[self.serializers.collection.to_collection_name(chart_params)]
		record = collection.find_one(sort = [ (Chart.timestamp_field, pymongo.ASCENDING) ])
		return normalize_timestamp(record[Chart.timestamp_field]) if record else None

	def backfill_worker(
		self,
		chart_params: ChartParams,
		repository: type[Repository],
	):
		logger.info(f'Backfilling chart:\n{pretty_repr(chart_params)}\n')
		repository = repository()
		new_data = repository.read_chart(chart_params)

		# Columns get processed into a MultiIndex we only need the fields not the time series names
		new_data.columns = [ column[-1] for column in new_data.columns ]
		self.write_chart(
			chart_params,
			data = new_data,
		)

	def backfill(
		self,
		chart: Chart = None,
		repository: type[Repository] = None,
		from_timestamp: pandas.Timestamp = None,
		to_timestamp: pandas.Timestamp = now(),
		clean: bool = False,
		workers: int = 1,
	):
		if clean:
			self.remove_historical_data(chart)

		pool = Pool(workers)
		try:
			if from_timestamp and to_timestamp:
				increments = list(pandas.date_range(
					start = from_timestamp,
					end = to_timestamp,
					freq = 'MS' # "Month Start"
				))
				# date_range where start - end < freq returns empty
				if len(increments) == 0:
					increments = [ from_timestamp, to_timestamp ]
				else:
					increments.append(to_timestamp)

					pool.starmap(
						self.backfill_worker,
						(
							(
								ChartParams(
									chart,
									{
										'from_timestamp' : increments[index - 1],
										'to_timestamp' : increments[index]
									},
								),
								repository
							)
							for index in range(1, len(increments))
						)
					)

			else:
				chart.read()
				self.write_chart(chart)
		finally:
			pool.close()
			pool.join()
	@property
	def historical_data(self):
		return self.client['historical_data']
