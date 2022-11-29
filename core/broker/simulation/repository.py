import os
import sys
import pandas
import pymongo
import logging

from core.interval import *
from core.chart import *
from core.utils.time import normalize_timestamp

logger = logging.getLogger(__name__)

class Repository:
	def __init__(self) -> None:
		self.client = pymongo.MongoClient(os.getenv('DB_URI'), tz_aware=True)

	def read_chart(
		self,
		chart: Chart,
		limit=0,
	) -> list[dict]:
		collection = self.get_collection_from_chart(chart)
		_filter = { 'timestamp' : {} }
		if chart.from_timestamp:
			_filter['timestamp']['$gte'] = chart.from_timestamp
		if chart.to_timestamp:
			_filter['timestamp']['$lte'] = chart.to_timestamp
		cursor = collection.find(_filter, limit=limit)
		return list(cursor)

	def write_chart(self, chart: Chart):
		collection = self.ensure_collection_for_chart(chart)
		data = chart.data

		if type(data) == pandas.DataFrame:
			rows = data.reset_index().to_dict(orient='records')
		else:
			rows = [
				dict(timestamp=timestamp, value=value)
				for timestamp, value in data.to_dict().items() 
			]

		duplicates = set()
		rows = [
			row for row in rows 
			if not (
				row['timestamp'] in duplicates 
				or duplicates.add(row['timestamp'])
			)
		]

		self.upsert(collection, rows)

	def upsert(self, collection, rows: list):
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
			self.write(collection, rows[start_from:])

	def get_collection_from_chart(self, chart: Chart):
		table = f"{type(chart).__name__}.{'.'.join([ str(getattr(chart, key)) for key in chart.query_fields ])}"
		return self.client['trading'][table]

	def get_chart_from_collection_name(self, name: str):
		chunks = name.split('.')
		return chunks

	def ensure_collection_for_chart(self, chart: Chart):
		collection = self.get_collection_from_chart(chart)
		index_information = collection.index_information()
		if 'timestamp' not in index_information:
			collection.create_index([('timestamp', pymongo.ASCENDING)], name='timestamp', unique=True)
		return collection

	def drop_collection_for_chart(self, chart: Chart):
		collection = self.get_collection_from_chart(chart)
		collection.drop()

	def get_available_charts(self):
		collection_names = self.client['trading'].list_collection_names()
		return [ self.get_chart_from_collection_name(name) for name in collection_names ]

	def get_max_available_timestamp_for_chart(self, chart: Chart):
		collection = self.get_collection_from_chart(chart)
		record = collection.find_one(sort=[('timestamp', pymongo.DESCENDING)])
		return normalize_timestamp(record['timestamp']) if record else None

	def get_min_available_timestamp_for_chart(self, chart: Chart):
		collection = self.get_collection_from_chart(chart)
		record = collection.find_one(sort=[('timestamp', pymongo.ASCENDING)])
		return normalize_timestamp(record['timestamp']) if record else None

	def write_backtest_report(self, report: dict):
		collection = self.client['trading_backtest_reports'][type(report['strategy']).__name__]
		report = self.encode(report)
		collection.insert_one(report)

	def encode(self, payload):
		# Exceptional non-primitive data types that pymongo can consume 
		if type(payload) in [ pandas.Timestamp ]:
			return payload

		# Data types that we don't have any other options for
		if type(payload) in [ pandas.Timedelta ]:
			return repr(payload)

		if type(payload) == list:
			return [ self.encode(item) for item in payload ]

		if type(payload) == dict:
			return { key: self.encode(payload[key]) for key in payload }

		if type(payload) == pandas.Series:
			return self.encode([
				dict(timestamp=timestamp, value=value)
				for timestamp, value in payload.to_dict().items() 
			])

		if type(payload) == pandas.DataFrame:
			return self.encode(payload.to_dict('records'))

		if hasattr(payload, '__dict__'):
			_dict: dict = payload.__dict__.copy()
			_dict['__repr__'] = repr(payload)

			# SHOULD DO: clean this up
			if 'broker' in _dict:
				_dict['broker'] = repr(_dict['broker'])
			if 'order' in _dict and _dict['order']:
				_dict['order'] = _dict['order'].id
			if 'position' in _dict and _dict['position']:
				_dict['position'] = _dict['position'].id
			return self.encode(_dict)
		return payload