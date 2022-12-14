from dataclasses import dataclass, field
import pymongo
import os

@dataclass
class MongoRepository:
	client: pymongo.MongoClient = field(default_factory=lambda: pymongo.MongoClient(os.getenv('DB_URI'), tz_aware=True))
