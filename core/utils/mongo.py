import pymongo
import os
import functools
from typing import Iterable

from pymongo.database import Database
from pymongo.errors import BulkWriteError
from pymongo.collection import Collection
from dataclasses import dataclass

from core.chart import Chart
from core.utils.logging import Logger

logger = Logger(__name__)

@dataclass
class MongoRepository:
	uri = os.getenv('DB_URI')

	@classmethod
	@property
	@functools.cache
	def client(self):
		return pymongo.MongoClient(self.uri, tz_aware = True)

	def upsert(
		self,
		collection: Collection,
		records: Iterable,
	):
		try:
			collection.insert_many(records, ordered = False)
		except BulkWriteError:
			pass # SHOULD DO: upsert: https://stackoverflow.com/questions/44838280/how-to-ignore-duplicate-key-errors-safely-using-insert-many

	def ensure_time_series_collection(
		self,
		database: Database,
		name: str
	):
		collection = database.get_collection(name)
		indexes = collection.index_information()

		if 'timestamp' not in indexes:
			collection.create_index(
				keys = [
					('timestamp', pymongo.ASCENDING)
				],
				name = 'timestamp',
				unique = True
			)

		return collection