import os

from typing import TypeVar
from datetime import date, datetime
from pandas import Timestamp
from dataclasses import dataclass

TimestampLike = TypeVar(
	'TimestampLike',
	str,
	Timestamp,
	date,
	datetime,
)

def now(tz='UTC'):
	return Timestamp.now(tz=os.getenv('TIMEZONE', 'EST')).tz_convert(tz)

def normalize_timestamp(timestamp: TimestampLike, tz='UTC'):
	if not timestamp:
		return None
	if type(timestamp) in[ datetime, date, str ]:
		timestamp = Timestamp(timestamp)
	if timestamp.tz:
		return timestamp.tz_convert(tz)
	return timestamp.tz_localize(tz)

@dataclass
class TimeWindow:
	from_timestamp: Timestamp = None
	to_timestamp: Timestamp = None

	def __post_init__(self):
		self.from_timestamp = normalize_timestamp(self.from_timestamp)
		self.to_timestamp = normalize_timestamp(self.to_timestamp)
