import os
import pandas

def now(tz='UTC'):
	return pandas.Timestamp.now(tz=os.getenv('TIMEZONE', 'EST')).tz_convert(tz)

def normalize_timestamp(timestamp: pandas.Timestamp or str, tz='UTC'):
	if not timestamp:
		return None
	if type(timestamp) == pandas.Timestamp:
		if timestamp.tz:
			return timestamp.tz_convert(tz)
		return timestamp.tz_localize(tz)
	return pandas.Timestamp(timestamp, tz=tz)
