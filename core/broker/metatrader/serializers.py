import typing
import pandas
from core.chart import Chart
from core.utils.serializer import Serializer

class MetaTraderCandleStickChartDataFrameSerializer(Serializer[pandas.DataFrame, typing.Any]):
	def deserialize(self, records, chart: Chart):
		dataframe = pandas.DataFrame(records)
		if 'time' in dataframe.columns:
			dataframe[Chart.timestamp_field] = pandas.to_datetime(dataframe['time'], unit='s', utc=True)
			dataframe = dataframe.drop(columns='time')

		dataframe = dataframe.drop(
			[
				column for column in dataframe.columns
				if column not in chart.select
			],
			axis=1
		)
		return dataframe

class MetaTraderTickChartDataFrameSerializer(Serializer[pandas.DataFrame, typing.Any]):
	def deserialize(self, records, chart: Chart):
		dataframe = pandas.DataFrame(records)

		if 'volume' in dataframe.columns and 'volume_real' in dataframe.columns:
			dataframe = dataframe.rename(columns={
				'volume': 'tick_volume',
				'volume_real': 'real_volume',
			})

		if 'time_msc' in dataframe.columns and 'time' in dataframe.columns:
			dataframe[Chart.timestamp_field] = pandas.to_datetime(dataframe['time_msc'], unit='ms', utc=True)
			dataframe = dataframe.drop(columns=[ 'time', 'time_msc' ])

		dataframe = dataframe.drop(
			[
				column for column in dataframe.columns
				if column not in chart.select
			],
			axis=1
		)

		return dataframe
