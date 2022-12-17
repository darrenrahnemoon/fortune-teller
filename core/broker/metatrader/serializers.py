import pandas
from core.chart import Chart
from core.chart.serializers import ChartDataFrameRecordsSerializer

class CandleStickChartDataFrameRecordsSerializer(ChartDataFrameRecordsSerializer):
	def to_dataframe(self, records, chart: Chart):
		dataframe = pandas.DataFrame(records)

		if 'time' in dataframe.columns:
			dataframe[Chart.timestamp_field] = pandas.to_datetime(dataframe['time'], unit='s')

		return super().to_dataframe(dataframe, chart)

class TickChartDataFrameRecordsSerializer(ChartDataFrameRecordsSerializer):
	def to_dataframe(self, records, chart: Chart):
		dataframe = pandas.DataFrame(records)

		dataframe = dataframe.rename(
			columns = {
				'volume': 'tick_volume',
				'volume_real': 'real_volume',
			}
		)

		if 'time_msc' in dataframe.columns:
			dataframe[Chart.timestamp_field] = pandas.to_datetime(dataframe['time_msc'], unit='ms')

		return super().to_dataframe(dataframe, chart)
