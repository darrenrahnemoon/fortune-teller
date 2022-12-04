import typing
import pandas
from core.utils.serializer import Serializer

class MetaTraderCandleStickChartDataFrameSerializer(Serializer[pandas.DataFrame, typing.Any]):
	def deserialize(self, value):
		dataframe = pandas.DataFrame(value)

		if 'time' in dataframe.columns:
			dataframe['timestamp'] = pandas.to_datetime(dataframe['time'], unit='s', utc=True)
			dataframe.drop(columns='time', inplace=True)

		return dataframe

class MetaTraderTickChartDataFrameSerializer(Serializer[pandas.DataFrame, typing.Any]):
	def deserialize(self, value):
		dataframe = pandas.DataFrame(value)

		if 'volume' in dataframe.columns and 'volume_real' in dataframe.columns:
			dataframe.rename(columns={
				'volume': 'tick_volume',
				'volume_real': 'real_volume',
			}, inplace=True)

		if 'time_msc' in dataframe.columns and 'time' in dataframe.columns:
			dataframe['timestamp'] = pandas.to_datetime(dataframe['time_msc'], unit='ms', utc=True)
			dataframe.drop(columns=[ 'time', 'time_msc' ], inplace=True)
		return dataframe
