import os
import pandas
import pymongo
import logging

from lib.chart import Chart

logger = logging.getLogger(__file__)

class Repository:
	def __init__(self) -> None:
		self.client = pymongo.MongoClient(os.getenv('DB_URI'), tz_aware=True)

	def get_collection_for(self, chart: Chart):
		database = os.getenv('DB_NAME', 'trading')
		table = f"{type(chart).__name__}.{'.'.join([ str(getattr(chart, key)) for key in chart.query_fields ])}"
		return self.client[database][table]

	def ensure_collection_configured_for(self, chart: Chart):
		collection = self.get_collection_for(chart)
		index_information = collection.index_information()
		logger.debug(f'Ensuring {collection} for {chart} is configured properly...\nCurrent Index Information:\n{index_information}')
		if 'timestamp' not in index_information:
			logger.debug('Creating a timestamp index...')
			collection.create_index([('timestamp', pymongo.ASCENDING)], name='timestamp', unique=True)

		return collection

	def read(self, chart: Chart) -> list[dict]:
		logger.debug(f'Reading {chart}...')
		collection = self.get_collection_for(chart)
		cursor = collection.find({
			'timestamp': {
				'$gte': chart.from_timestamp,
				'$lte': chart.to_timestamp,
			}
		})
		records = list(cursor)
		logger.debug(f'Read records. Sample:\n{records[0] if len(records) else None}')
		return records

	def write(self, chart: Chart):
		logger.debug(f'Writing {chart}...')
		collection = self.ensure_collection_configured_for(chart)
		data = chart.data
		if type(data) == pandas.DataFrame:
			rows = data.to_dict(orient='records')
		else:
			rows = [
				dict(timestamp=timestamp, value=value)
				for timestamp, value in data.to_dict().items() 
			]

		for row in rows:
			collection.replace_one({ 'timestamp': row['timestamp'] }, row, upsert=True)

	def get_max_timestamp(self, chart: Chart):
		collection = self.get_collection_for(chart)
		cursor = collection.find().sort({ 'timestamp': pymongo.DESCENDING }).limit(1)
		result = list(cursor)
		return pandas.Timestamp(result[0]['timestamp'] if len(result) else 0)

	def get_min_timestamp(self, chart: Chart):
		collection = self.get_collection_for(chart)
		cursor = collection.find().sort({ 'timestamp': pymongo.ASCENDING }).limit(1)
		result = list(cursor)
		return pandas.Timestamp(result[0]['timestamp'] if len(result) else 0)