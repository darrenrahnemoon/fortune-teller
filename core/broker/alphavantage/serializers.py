import pandas
from core.chart import Chart
from core.chart.serializers import ChartDataFrameRecordsSerializer

class LineChartDataFrameRecordsSerializer(ChartDataFrameRecordsSerializer):
	def to_dataframe(self, records, chart):
		dataframe = pandas.DataFrame.from_records(records, index='date')

		dataframe = dataframe[dataframe['value'] != '.']
		dataframe['value'] = dataframe['value'].astype(float)

		dataframe.index = pandas.to_datetime(dataframe.index)
		dataframe.index.name = Chart.timestamp_field
		dataframe = dataframe.reindex(index = dataframe.index[::-1])

		return super().to_dataframe(dataframe, chart)