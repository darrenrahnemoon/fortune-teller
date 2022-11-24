from pymongo import collection
from lib.utils.time import normalize_timestamp
import os
import pandas
import pymongo
import logging

from lib.chart import Chart

logger = logging.getLogger(__name__)

class Repository:
	def __init__(self) -> None:
		self.client = pymongo.MongoClient(os.getenv('DB_URI'), tz_aware=True)

	def read(
		self,
		chart: Chart,
		limit=0,
	) -> list[dict]:
		collection = self.get_collection_for(chart)
		_filter = { 'timestamp' : {} }
		if chart.from_timestamp:
			_filter['timestamp']['$gte'] = chart.from_timestamp
		if chart.to_timestamp:
			_filter['timestamp']['$lte'] = chart.to_timestamp
		cursor = collection.find(_filter, limit=limit)
		return list(cursor)

	def write(self, chart: Chart):
		collection = self.ensure_collection_configured_for(chart)
		data = chart.data
		if type(data) == pandas.DataFrame:
			rows = data.reset_index().to_dict(orient='records')
		else:
			rows = [
				dict(timestamp=timestamp, value=value)
				for timestamp, value in data.to_dict().items() 
			]
		try:
			collection.insert_many(rows)
		except:
			rows = [
				pymongo.UpdateOne(
					{ 'timestamp': row['timestamp'] },
					{ '$set' : row },
					upsert=True
				)
				for row in rows
			]
			collection.bulk_write(rows)

	def get_max_timestamp(self, chart: Chart):
		collection = self.get_collection_for(chart)
		record = collection.find_one(sort=[('timestamp', pymongo.DESCENDING)])
		return normalize_timestamp(record['timestamp']) if record else None

	def get_min_timestamp(self, chart: Chart):
		collection = self.get_collection_for(chart)
		record = collection.find_one(sort=[('timestamp', pymongo.ASCENDING)])
		return normalize_timestamp(record['timestamp']) if record else None

	def get_collection_for(self, chart: Chart):
		database = os.getenv('DB_NAME', 'trading')
		table = f"{type(chart).__name__}.{'.'.join([ str(getattr(chart, key)) for key in chart.query_fields ])}"
		return self.client[database][table]

	def drop_collection_for(self, chart: Chart):
		collection = self.get_collection_for(chart)
		collection.drop()

	def ensure_collection_configured_for(self, chart: Chart):
		collection = self.get_collection_for(chart)
		index_information = collection.index_information()
		if 'timestamp' not in index_information:
			collection.create_index([('timestamp', pymongo.ASCENDING)], name='timestamp', unique=True)
		return collection