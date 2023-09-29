import pandas
from typing import Iterable
from dataclasses import dataclass, fields, field

from core.utils.collection import is_any_of
from core.chart import Chart
from core.utils.serializer import Serializer
from core.utils.logging import Logger

logger = Logger(__name__)

MULTI_INDEX_COLUMN_SEPARATOR = '/'

@dataclass
class ChartRecordsSerializer(Serializer):
	chart_class: type[Chart] = field(default_factory = lambda : Chart)

	def to_dataframe(
		self,
		value: pandas.DataFrame or Iterable,
		name: str = None,
		select: list[str] = None,
		tz = 'UTC',
	) -> pandas.DataFrame:
		# Note: this serializer is the only serializer that will mutate the records if given a dataframe

		# Convert records to dataframe if it's already not
		dataframe = value
		if not isinstance(value, (pandas.DataFrame, pandas.Series)):
			if hasattr(value, '__iter__'):
				if type(value) != list:
					value = list(value)
					# pandas.DataFrame constructor doesn't directly accept iterators
					dataframe = pandas.DataFrame.from_records(value)

		# Skip if not a dataframe
		if type(dataframe) != pandas.DataFrame:
			if dataframe != None: # None is expected occasionally
				logger.warn(f'Unrecognized value passed to {type(self).__name__}.to_dataframe:\n{dataframe}')
			return dataframe

		# Empty dataframes might not have the right columns, so add them
		if len(dataframe) == 0 and type(dataframe.columns) != pandas.MultiIndex: # NOTE: `select` not supported for MultiIndex columns
			dataframe['timestamp'] = None
			if select and len(select):
				dataframe[select] = None

		# Ensure timestamp is index
		if type(dataframe.index) != pandas.DatetimeIndex:
			dataframe.index = pandas.DatetimeIndex(dataframe['timestamp'], name = 'timestamp')
			dataframe = dataframe.drop(columns = [ 'timestamp' ])

		# Make sure the dataframe is ascending
		if len(dataframe.index) > 1 and dataframe.index[0] > dataframe.index[-1]:
			dataframe = dataframe.sort_index(ascending = True)

		# Ensure timestamp is timezone aware since different brokers have different time zones
		if not dataframe.index.tz:
			dataframe.index = dataframe.index.tz_localize(tz = tz)

		# Unflatten columns if columns are flattened
		if is_any_of(dataframe.columns, lambda column: MULTI_INDEX_COLUMN_SEPARATOR in column and type(column) == str):
			dataframe.columns = pandas.MultiIndex.from_tuples([ column.split(MULTI_INDEX_COLUMN_SEPARATOR) for column in dataframe.columns ])

		# set column types from Chart.Record schema
		for field in fields(self.chart_class.Record):
			if not field.name in dataframe.columns:
				continue

			if dataframe.dtypes[field.name] == field.type:
				continue
			try:
				dataframe[field.name] = dataframe[field.name].astype(field.type)
			except:
				logger.warn(f"Unable to cast field '{field.name}' from '{dataframe.dtypes[field.name]}' to '{field.type}'.")

		# Add the wrapping column based on the chart specified
		if type(dataframe.columns) != pandas.MultiIndex:
			if select and len(select):
				dataframe = dataframe[[ key for key in dataframe.columns if key in select ]]

			if name:
				dataframe.columns = pandas.MultiIndex.from_tuples(
					[ (name, column) for column in dataframe.columns ],
					names=[ 'chart', 'field' ]
				)

		return dataframe

	def to_records(self, dataframe: pandas.DataFrame):
		if type(dataframe.columns) == pandas.MultiIndex:
			dataframe.columns = [ MULTI_INDEX_COLUMN_SEPARATOR.join(filter(None, column)) for column in dataframe.columns ]

		return dataframe \
			.reset_index() \
			.drop_duplicates('timestamp') \
			.to_dict(orient='records')
