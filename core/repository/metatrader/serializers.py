import pandas

from core.chart import Chart
from core.utils.serializer import MappingSerializer
from core.chart.serializers import ChartDataFrameRecordsSerializer
from core.interval import Interval

class CandleStickChartDataFrameRecordsSerializer(ChartDataFrameRecordsSerializer):
	def to_dataframe(self, records, **kwargs):
		dataframe = pandas.DataFrame(records)

		dataframe = dataframe.rename(
			columns = {
				'tick_volume': 'volume_tick',
				'real_volume': 'volume_real',
			}
		)

		# make sure a `timestamp` field is present so it becomes an index later
		if 'time' in dataframe.columns:
			dataframe[Chart.timestamp_field] = pandas.to_datetime(dataframe['time'], unit='s')

		return super().to_dataframe(dataframe, **kwargs)

class TickChartDataFrameRecordsSerializer(ChartDataFrameRecordsSerializer):
	def to_dataframe(self, records, **kwargs):
		dataframe = pandas.DataFrame(records)

		# standardize the columns
		dataframe = dataframe.rename(
			columns = {
				'volume': 'volume_tick',
				'volume_real': 'volume_real',
			}
		)

		# make sure a `timestamp` field is present so it becomes an index later
		if 'time_msc' in dataframe.columns:
			dataframe[Chart.timestamp_field] = pandas.to_datetime(dataframe['time_msc'], unit='ms')

		return super().to_dataframe(dataframe, **kwargs)

class MetaTraderRecordsSerializers:
	candlestick = CandleStickChartDataFrameRecordsSerializer()
	tick = TickChartDataFrameRecordsSerializer()

class MetaTraderSerializers:
	records = MetaTraderRecordsSerializers()
	interval = MappingSerializer({
		Interval.Minute(1) : 1,
		Interval.Minute(2) : 2,
		Interval.Minute(3) : 3,
		Interval.Minute(4) : 4,
		Interval.Minute(5) : 5,
		Interval.Minute(6) : 6,
		Interval.Minute(10) : 10,
		Interval.Minute(12) : 12,
		Interval.Minute(15) : 15,
		Interval.Minute(20) : 20,
		Interval.Minute(30) : 30,
		Interval.Hour(1) : 1 | 0x4000,
		Interval.Hour(2) : 2 | 0x4000,
		Interval.Hour(4) : 4 | 0x4000,
		Interval.Hour(3) : 3 | 0x4000,
		Interval.Hour(6) : 6 | 0x4000,
		Interval.Hour(8) : 8 | 0x4000,
		Interval.Hour(12) : 12 | 0x4000,
		Interval.Day(1) : 24| 0x4000,
		Interval.Week(1) : 1 | 0x8000,
		Interval.Month(1) : 1 | 0xC000,
	})
