import pandas

from core.utils.collection import is_any_of
from core.chart import Chart, ChartGroup
from core.utils.serializer import Serializer

MULTI_INDEX_COLUMN_SEPARATOR = ','

class ChartDataFrameRecordsSerializer(Serializer):
	# Note: this serializer is the only serializer that will mutate the dataframe
	def to_dataframe(self, value: pandas.DataFrame or list, chart: Chart = None) -> pandas.DataFrame:
		# Convert records to dataframe
		if type(value) == list:
			value = pandas.DataFrame.from_records(value)

		# Skip if not a dataframe
		if type(value) != pandas.DataFrame:
			return value

		# Empty dataframes might not have the right columns
		if len(value) == 0:
			value = pandas.DataFrame(columns = [ Chart.timestamp_field ])

		# Clean up timestamp
		if type(value.index) != pandas.DatetimeIndex:
			value.index = pandas.DatetimeIndex(value[Chart.timestamp_field], name=Chart.timestamp_field)
			value = value.drop(columns=[ Chart.timestamp_field ])
		if not value.index.tz:
			value.index = value.index.tz_localize(tz='UTC')

		# Unflatten columns if columns are flattened
		if is_any_of(value.columns, lambda column: MULTI_INDEX_COLUMN_SEPARATOR in column and column != '_id'): # HACK: mongo id returns a false positive for this
			value.columns = pandas.MultiIndex.from_tuples([ column.split(MULTI_INDEX_COLUMN_SEPARATOR) for column in value.columns ])

		# Add the wrapping column based on the chart specified
		if type(value.columns) != pandas.MultiIndex:
			value = value[[ key for key in value.columns if key in chart.select ]]
			value.columns = pandas.MultiIndex.from_tuples(
				[ (chart.name, column) for column in value.columns ],
				names=[ 'timeseries', 'field' ]
			)
		return value

	def to_records(self, dataframe: pandas.DataFrame or Chart or ChartGroup):
		if isinstance(dataframe, Chart) or isinstance(dataframe, ChartGroup):
			dataframe = dataframe.dataframe

		if type(dataframe.columns) == pandas.MultiIndex:
			dataframe.columns = [ MULTI_INDEX_COLUMN_SEPARATOR.join(filter(None, column)) for column in dataframe.columns ]

		return dataframe \
			.reset_index() \
			.drop_duplicates(Chart.timestamp_field) \
			.to_dict(orient='records')
