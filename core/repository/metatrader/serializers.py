import pandas
import MetaTrader5
from dataclasses import field, dataclass

from core.chart import CandleStickChart, TickChart
from core.utils.serializer import MappingSerializer
from core.chart.serializers import ChartRecordsSerializer
from core.interval import Interval

@dataclass
class CandleStickChartRecordsSerializer(ChartRecordsSerializer):
	chart_class: type[CandleStickChart] = field(default_factory = lambda : CandleStickChart)

	def to_dataframe(self, records, *args, **kwargs):
		dataframe = pandas.DataFrame(records)

		dataframe = dataframe.rename(
			columns = {
				'tick_volume': 'volume_tick',
				'real_volume': 'volume_real',
			}
		)

		# Metatrader provides spread in points
		if 'spread' in dataframe.columns:
			dataframe['spread_pips'] = dataframe['spread'] / 10
			dataframe = dataframe.drop('spread', axis = 1)

		# make sure a `timestamp` field is present so it becomes an index later
		if 'time' in dataframe.columns:
			dataframe['timestamp'] = pandas.to_datetime(dataframe['time'], unit='s')
			dataframe = dataframe.drop('time', axis = 1)

		return super().to_dataframe(dataframe, *args, **kwargs)

@dataclass
class TickChartRecordsSerializer(ChartRecordsSerializer):
	chart_class: type[TickChart] = field(default_factory = lambda : TickChart)

	def to_dataframe(self, records, *args, **kwargs):
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
			dataframe['timestamp'] = pandas.to_datetime(dataframe['time_msc'], unit='ms')
			dataframe = dataframe.drop('time_msc', axis = 1)

		if 'time' in dataframe.columns:
			dataframe = dataframe.drop('time', axis = 1)

		return super().to_dataframe(dataframe, *args, **kwargs)


class MetaTraderSerializers:
	records = {
		TickChart : TickChartRecordsSerializer(),
		CandleStickChart : CandleStickChartRecordsSerializer()
	}
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
