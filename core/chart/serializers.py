import pandas
from collections import defaultdict

from core.chart import Chart, ChartGroup
from core.utils.serializer import Serializer

class ChartDataFrameRecordsSerializer(Serializer):
	# Note: this serializer is the only serializer that mutates mutates the dataframe
	def to_dataframe(self, dataframe: pandas.DataFrame or list, chart: Chart) -> pandas.DataFrame:
		if type(dataframe) == list:
			dataframe = pandas.DataFrame.from_records(
				dataframe,
				columns = [ Chart.timestamp_field ] + chart.select
			)

		if type(dataframe) != pandas.DataFrame:
			return dataframe

		if len(dataframe) == 0:
			dataframe = pandas.DataFrame(columns = [ Chart.timestamp_field ] + chart.select)

		if type(dataframe.index) != pandas.DatetimeIndex:
			dataframe.index = pandas.DatetimeIndex(dataframe[Chart.timestamp_field], name=Chart.timestamp_field)
	
		if not dataframe.index.tz:
			dataframe.index = dataframe.index.tz_localize(tz='UTC')

		if type(dataframe.columns) != pandas.MultiIndex:
			dataframe = dataframe[[ key for key in dataframe.columns if key in chart.select ]]
			dataframe.columns = pandas.MultiIndex.from_tuples(
				[ (chart.name, column) for column in dataframe.columns ],
				names=[ 'timeseries', 'field' ]
			)
		return dataframe

	def to_records(self, dataframe: pandas.DataFrame or Chart or ChartGroup):
		if isinstance(dataframe, Chart) or isinstance(dataframe, ChartGroup):
			dataframe = dataframe.dataframe

		rows = dataframe.reset_index()\
			.drop_duplicates(Chart.timestamp_field)\
			.to_dict(orient='records')

		if type(next(iter(rows[0]))) == tuple:
			result = []
			for row in rows:
				item = defaultdict(dict)
				for key, value in row.items():
					item[key[0]][key[1]] = value
			return result

		return rows
