import pandas
import pymongo
from pymongo.collection import Collection
from multiprocess import Pool
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .serializers import SimulationSerializers
from core.chart import Chart, ChartGroup, OverriddenChart, CandleStickChart
from core.repository.repository import Repository
from core.interval import Interval
from core.utils.time import TimeWindow, normalize_timestamp
from core.utils.mongo import MongoRepository
from core.utils.logging import Logger
from core.utils.cls.repr import pretty_repr
from core.utils.time import TimestampLike, now
if TYPE_CHECKING:
	from core.order import OrderType

logger = Logger(__name__)

@dataclass
class SimulationRepository(Repository, MongoRepository):
	serializers = SimulationSerializers()

	def __post_init__(self):
		self._now = None

	@property
	def now(self) -> pandas.Timestamp:
		return self._now or super().now

	@now.setter
	def now(self, value: TimestampLike):
		self._now = normalize_timestamp(value)

	def read_chart(
		self,
		chart: Chart or OverriddenChart = None,
		collection: str = None,
		database: str = None,
		**overrides
	) -> pandas.DataFrame:
		database = self.client[database] if database else self.historical_data
		chart = OverriddenChart(chart, overrides)
		find_options = self.serializers.find_options.to_find_options(chart)

		collection = collection or self.serializers.collection.to_collection_name(chart)
		collection = database.get_collection(collection)
		records = collection.find(**find_options)

		dataframe = self.serializers.records.to_dataframe(
			records,
			name = chart.name,
			select = chart.select
		)

		logger.debug(f'Read chart:\n{dataframe}')
		return dataframe

	def get_last_price(
		self,
		symbol,
		timestamp: pandas.Timestamp = None,
		intent: 'OrderType' = None,
	) -> float:
		if timestamp == None:
			timestamp = self.now
		chart = CandleStickChart(
			symbol = symbol,
			interval = Interval.Minute(1),
			count = 1,
			to_timestamp = timestamp,
			repository = self
		).read()
		return chart.data['close'].iloc[0]

	def write_chart(
		self,
		chart: Chart or OverriddenChart = None,
		collection: str = None,
		database: str = None,
		**overrides
	):
		chart = OverriddenChart(chart, overrides)
		database = self.client[database] if database else self.historical_data
		data = chart.data
		if len(data) == 0:
			logger.warn(f"Attempted to write an empty {chart.name} into database. Skipping...")
			return

		logger.debug(f'Writing chart:\n{data}')
		collection = collection or self.serializers.collection.to_collection_name(chart)
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
		chart: Chart or OverriddenChart = None,
		**overrides
	):
		chart = OverriddenChart(chart, overrides)
		collection = self.serializers.collection.to_collection_name(chart)
		self.historical_data.drop_collection(collection)

	def get_common_time_window(
		self,
		chart_group: ChartGroup or OverriddenChart or list[Chart]= None,
		**overrides
	) -> TimeWindow:
		if type(chart_group) == ChartGroup:
			chart_group = OverriddenChart(chart_group, overrides)

		if type(chart_group) == OverriddenChart:
			charts = chart_group.charts
		elif type(chart_group) == list:
			charts = chart_group
		else:
			raise Exception(f"Invalid parameter 'chart_group'. Received {chart_group}.")

		from_timestamp = []
		to_timestamp = []
		for chart in charts:
			from_timestamp.append(self.get_min_available_timestamp(chart))
			to_timestamp.append(self.get_max_available_timestamp(chart))

		return TimeWindow(
			from_timestamp = max(from_timestamp),
			to_timestamp = min(to_timestamp)
		)

	def get_all_available_charts(self, include_timestamps = False, **kwargs):
		collection_names = self.historical_data.list_collection_names()
		collection_names.sort()
		for name in collection_names:
			chart = self.serializers.collection.to_chart(name)
			if include_timestamps:
				chart.from_timestamp = self.get_min_available_timestamp(chart)
				chart.to_timestamp = self.get_max_available_timestamp(chart)
			yield chart

	def count_available_data_points(
		self,
		chart: Chart or OverriddenChart = None,
		**overrides,
	):
		chart = OverriddenChart(chart, overrides)
		collection: Collection = self.historical_data[self.serializers.collection.to_collection_name(chart)]
		find_options = self.serializers.find_options.to_find_options(chart)
		return collection.count_documents(filter = find_options['filter'])

	def get_gap_percentage(
		self,
		chart: Chart or OverriddenChart = None,
		**overrides,
	):
		chart = OverriddenChart(chart, overrides)
		delta = chart.to_timestamp - chart.from_timestamp
		expected_data_points_count = delta / chart.interval.to_pandas_timedelta()
		current_data_points_count = self.count_available_data_points(chart)
		return (1 - (current_data_points_count / expected_data_points_count))

	def get_max_available_timestamp(
		self,
		chart: Chart or OverriddenChart = None,
		**overrides
	) -> pandas.Timestamp:
		chart = OverriddenChart(chart, overrides)
		collection = self.historical_data[self.serializers.collection.to_collection_name(chart)]
		record = collection.find_one(sort = [ (Chart.timestamp_field_name, pymongo.DESCENDING) ])
		return normalize_timestamp(record[Chart.timestamp_field_name]) if record else None

	def get_min_available_timestamp(
		self,
		chart: Chart or OverriddenChart = None,
		**overrides
	) -> pandas.Timestamp:
		chart = OverriddenChart(chart, overrides)
		collection = self.historical_data[self.serializers.collection.to_collection_name(chart)]
		record = collection.find_one(sort = [ (Chart.timestamp_field_name, pymongo.ASCENDING) ])
		return normalize_timestamp(record[Chart.timestamp_field_name]) if record else None

	def backfill_worker(
		self,
		chart: Chart,
		overrides: dict,
		repository: type[Repository],
	):
		chart = OverriddenChart(chart, overrides)
		logger.info(f'Backfilling chart:\n{pretty_repr(chart)}\n')
		repository = repository()
		new_data = repository.read_chart(chart)

		# Columns get processed into a MultiIndex we only need the fields not the time series names
		new_data.columns = [ column[-1] for column in new_data.columns ]
		self.write_chart(
			chart,
			data = new_data,
		)

	def backfill(
		self,
		chart: Chart = None,
		repository: type[Repository] = None,
		from_timestamp: pandas.Timestamp = None,
		to_timestamp: pandas.Timestamp = None,
		clean: bool = False,
		workers: int = 1,
		batch_size: Interval = None,
	):
		to_timestamp = to_timestamp or now()
		if clean:
			self.remove_historical_data(chart)

		with Pool(workers) as pool:
			increments = list(pandas.date_range(
				start = from_timestamp,
				end = to_timestamp,
				freq = batch_size.to_pandas_frequency() # "Month Start"
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
							chart,
							{
								'from_timestamp' : increments[index - 1],
								'to_timestamp' : increments[index]
							},
							repository
						)
						for index in range(1, len(increments))
					)
				)

	@property
	def historical_data(self):
		return self.client['historical_data']
