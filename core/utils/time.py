import datetime
import os
import pandas

def now(tz='UTC'):
	return pandas.Timestamp.now(tz=os.getenv('TIMEZONE', 'EST')).tz_convert(tz)

def normalize_timestamp(timestamp: str or pandas.Timestamp or datetime.datetime, tz='UTC'):
	if not timestamp:
		return None
	if type(timestamp) in[datetime.datetime, str]:
		timestamp = pandas.Timestamp(timestamp)
	if timestamp.tz:
		return timestamp.tz_convert(tz)
	return timestamp.tz_localize(tz)
