import pandas
from core.utils.serializer import Serializer

class AlphaVantageLineChartDataFrameSerializer(Serializer[pandas.DataFrame, list[dict[str]]]):
	def deserialize(self, records):
		dataframe = pandas.DataFrame.from_records(records, index='date')

		# Value-related transformations
		dataframe = dataframe[dataframe['value'] != '.']
		dataframe['value'] = dataframe['value'].astype(float)

		# Timestamp-related transformations
		dataframe.index = pandas.to_datetime(dataframe.index)
		dataframe.index.name = 'timestamp'
		dataframe = dataframe.reindex(index=dataframe.index[::-1])
		return dataframe
