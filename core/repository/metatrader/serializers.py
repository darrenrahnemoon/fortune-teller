import pandas
import MetaTrader5

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
			dataframe[Chart.timestamp_field_name] = pandas.to_datetime(dataframe['time'], unit='s')
			dataframe = dataframe.drop('time', axis = 1)

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
			dataframe[Chart.timestamp_field_name] = pandas.to_datetime(dataframe['time_msc'], unit='ms')
			dataframe = dataframe.drop('time_msc', axis = 1)

		if 'time' in dataframe.columns:
			dataframe = dataframe.drop('time', axis = 1)

		return super().to_dataframe(dataframe, **kwargs)

class MetaTraderRecordsSerializers:
	candlestick = CandleStickChartDataFrameRecordsSerializer()
	tick = TickChartDataFrameRecordsSerializer()

class MetaTraderSerializers:
	records = MetaTraderRecordsSerializers()
	interval = MappingSerializer({
		Interval.Minute(1) : MetaTrader5.TIMEFRAME_M1,
		Interval.Minute(2) : MetaTrader5.TIMEFRAME_M2,
		Interval.Minute(3) : MetaTrader5.TIMEFRAME_M3,
		Interval.Minute(4) : MetaTrader5.TIMEFRAME_M4,
		Interval.Minute(5) : MetaTrader5.TIMEFRAME_M5,
		Interval.Minute(6) : MetaTrader5.TIMEFRAME_M6,
		Interval.Minute(10) : MetaTrader5.TIMEFRAME_M10,
		Interval.Minute(12) : MetaTrader5.TIMEFRAME_M12,
		Interval.Minute(15) : MetaTrader5.TIMEFRAME_M15,
		Interval.Minute(20) : MetaTrader5.TIMEFRAME_M20,
		Interval.Minute(30) : MetaTrader5.TIMEFRAME_M30,
		Interval.Hour(1) : MetaTrader5.TIMEFRAME_H1,
		Interval.Hour(2) : MetaTrader5.TIMEFRAME_H2,
		Interval.Hour(4) : MetaTrader5.TIMEFRAME_H4,
		Interval.Hour(3) : MetaTrader5.TIMEFRAME_H3,
		Interval.Hour(6) : MetaTrader5.TIMEFRAME_H6,
		Interval.Hour(8) : MetaTrader5.TIMEFRAME_H8,
		Interval.Hour(12) : MetaTrader5.TIMEFRAME_H2,
		Interval.Day(1) : MetaTrader5.TIMEFRAME_D1,
		Interval.Week(1) : MetaTrader5.TIMEFRAME_W1,
		Interval.Month(1) : MetaTrader5.TIMEFRAME_MN1,
	})
