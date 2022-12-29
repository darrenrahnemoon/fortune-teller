import logging
import pandas
from typing import Iterable

from core.utils.collection import is_any_of
from core.chart import Chart
from core.utils.serializer import Serializer

logger = logging.getLogger(__name__)

MULTI_INDEX_COLUMN_SEPARATOR = '/'

class ChartDataFrameRecordsSerializer(Serializer):
	def to_dataframe(
		self,
		value: pandas.DataFrame or Iterable,
		name: str = None,
		select: list[str] = None,
		tz = 'UTC',
	) -> pandas.DataFrame:
		# Note: this serializer is the only serializer that will mutate the records if given a dataframe

		# Convert records to dataframe
		if hasattr(value, '__iter__'):
			if not isinstance(value, (pandas.DataFrame, pandas.Series)):
				if type(value) != list:
					value = list(value)
					# pandas doesn't accept iterators
					value = pandas.DataFrame.from_records(value)

		# Skip if not a dataframe
		if type(value) != pandas.DataFrame:
			if value != None: # None is expected occasionally
				logger.warn(f'Unrecognized value passed to {type(self).__name__}.to_dataframe:\n{value}')
			return value

		# Empty dataframes might not have the right columns, so add them
		if len(value) == 0 and type(value.columns) != pandas.MultiIndex: # NOTE: `select` not supported for MultiIndex columns
			value[[ Chart.to_timestamp ] + (select or [])] = None # by setting to None the columns are "upserted"

		# Ensure timestamp is index
		if type(value.index) != pandas.DatetimeIndex:
			value.index = pandas.DatetimeIndex(value[Chart.timestamp_field], name = Chart.timestamp_field)
			value = value.drop(columns = [ Chart.timestamp_field ])

		# Ensure timestamp is timezone aware since different brokers have different time zones
		if not value.index.tz:
			value.index = value.index.tz_localize(tz = tz)

		# Unflatten columns if columns are flattened
		if is_any_of(value.columns, lambda column: MULTI_INDEX_COLUMN_SEPARATOR in column and type(column) == str):
			value.columns = pandas.MultiIndex.from_tuples([ column.split(MULTI_INDEX_COLUMN_SEPARATOR) for column in value.columns ])

		# Add the wrapping column based on the chart specified
		if type(value.columns) != pandas.MultiIndex:
			if select and len(select):
				value = value[[ key for key in value.columns if key in select ]]

			if name:
				value.columns = pandas.MultiIndex.from_tuples(
					[ (name, column) for column in value.columns ],
					names=[ 'timeseries', 'field' ]
				)
		return value

	def to_records(self, dataframe: pandas.DataFrame):
		if type(dataframe.columns) == pandas.MultiIndex:
			dataframe.columns = [ MULTI_INDEX_COLUMN_SEPARATOR.join(filter(None, column)) for column in dataframe.columns ]

		return dataframe \
			.reset_index() \
			.drop_duplicates(Chart.timestamp_field) \
			.to_dict(orient='records')
