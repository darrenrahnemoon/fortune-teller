import pandas
import pymongo
import logging
from dataclasses import dataclass

from core.chart import ChartGroup, Chart
from core.chart.serializers import ChartDataFrameRecordsSerializer
from core.broker.simulation.serializers import ChartCollectionSerializer, ChartMongoFindOptionsSerializer
from core.utils.mongo import MongoRepository
from .preprocessor import NextPeriodHighLowPreprocessor

logger = logging.getLogger(__name__)

@dataclass
class NextPeriodHighLowRepository(MongoRepository):
	preprocessor: NextPeriodHighLowPreprocessor = None
	dataframe_records_serializer = ChartDataFrameRecordsSerializer()
	chart_collection_serializer = ChartCollectionSerializer()
	mongo_find_options_serializer = ChartMongoFindOptionsSerializer()

	def ensure_collection_for_chart_group(self, chart_group: ChartGroup):
		collection = self.training_datasets[self.chart_collection_serializer.to_collection_name(chart_group)]

		if Chart.timestamp_field not in collection.index_information():
			collection.create_index([(Chart.timestamp_field, pymongo.ASCENDING)], name=Chart.timestamp_field, unique=True)

		return collection

	def read_chart_group_raw(self, chart_group: ChartGroup) -> list:
		collection = self.training_datasets[self.chart_collection_serializer.to_collection_name(chart_group)]
		return list(collection.find(**self.mongo_find_options_serializer.to_find_options(chart_group)))

	def read_chart_group(self, chart_group: ChartGroup) -> pandas.DataFrame:
		records = self.read_chart_group_raw(chart_group)
		return self.dataframe_records_serializer.to_dataframe(records, chart_group)

	def write_chart_group(self, chart_group: ChartGroup):
		if len(chart_group.dataframe) == 0:
			logger.warn(f'Attempted to write an empty {chart_group} into database. Skipping...')
			return

		collection = self.ensure_collection_for_chart_group(chart_group)
		rows = self.dataframe_records_serializer.to_records(chart_group.dataframe)
		self.upsert(collection, rows)

	@property
	def training_datasets(self):
		return self.client['training_datasets']
