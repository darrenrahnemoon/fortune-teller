import pandas
from typing import Iterable
from core.utils.serializer import MappingSerializer
from core.chart.serializers import ChartDataFrameRecordsSerializer
from core.chart import Chart
from core.interval import Interval

class LineChartDataFrameRecordsSerializer(ChartDataFrameRecordsSerializer):
	def to_dataframe(self, records: Iterable[dict], **kwargs):
		dataframe = pandas.DataFrame.from_records(records, index='date')

		dataframe = dataframe[dataframe['value'] != '.']
		dataframe['value'] = dataframe['value'].astype(float)

		dataframe.index = pandas.to_datetime(dataframe.index)
		dataframe.index.name = Chart.timestamp_field_name

		# revert the order to ascending as the AlphaVantage API gives descending data
		dataframe = dataframe.reindex(index = dataframe.index[::-1])

		return super().to_dataframe(dataframe, **kwargs)

class AlphaVantageSerializers:
	records = LineChartDataFrameRecordsSerializer()
	interval = MappingSerializer({
		Interval.Day(1): 'daily',
		Interval.Week(1): 'weekly',
		Interval.Month(1): 'monthly',
		Interval.Quarter(1): 'quarterly',
		Interval.Month(6) : 'semiannual',
		Interval.Year(1): 'annual',
	})
	treasury_yield_maturity = MappingSerializer({
		Interval.Month(3): '3month',
		Interval.Year(2): '2year',
		Interval.Year(5): '5year',
		Interval.Year(7): '7year',
		Interval.Year(10): '10year',
		Interval.Year(30): '30year',
	})
