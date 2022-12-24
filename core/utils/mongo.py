import sys
import pymongo
import os
import logging
import functools
from pymongo.collection import Collection
from dataclasses import dataclass

from core.chart import Chart

logger = logging.getLogger(__name__)

@dataclass
class MongoRepository:
	uri = os.getenv('DB_URI')

	@classmethod
	@property
	@functools.cache
	def client(self):
		return pymongo.MongoClient(self.uri, tz_aware=True)

	def upsert(self, collection: Collection, rows: list):
		try:
			collection.insert_many(rows)
		except:
			index = sys.exc_info()[1].details['writeErrors'][0]['index']
			failed_row = rows[index]
			del failed_row['_id'] # Cannot upsert a new generated `_id` on existing document

			logger.debug(f"Duplicated row found. Upserting...\n{failed_row[Chart.timestamp_field]}")
			collection.update_one({ Chart.timestamp_field: failed_row[Chart.timestamp_field] }, { '$set' : failed_row })

			start_from = index + 1
			if start_from == len(rows):
				return
			self.upsert(collection, rows[start_from:])
