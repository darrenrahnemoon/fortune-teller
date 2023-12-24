import pandas
from dataclasses import dataclass, field
from typing import Iterable
from core.utils.serializer import MappingSerializer
from core.trading.chart.serializers import ChartRecordsSerializer
from core.trading.chart import LineChart
from core.trading.interval import Interval

@dataclass
class LineChartRecordsSerializer(ChartRecordsSerializer):
	chart_class: type[LineChart] = field(default_factory = lambda : LineChart)

	def to_dataframe(self, records: Iterable[dict], *args, **kwargs):
		dataframe = pandas.DataFrame.from_records(records)

		dataframe = dataframe.rename(
			columns = {
				'date' : 'timestamp'
			}
		)

		# Remove null values that are specified as '.' by Alphavantage
		dataframe = dataframe[dataframe['value'] != '.']

		dataframe = super().to_dataframe(dataframe, *args, **kwargs)

		# Alphavantage gives results in descending order. Switch to ascending
		dataframe = dataframe.sort_values(
			by = 'timestamp',
			ascending = True
		)

		return dataframe

class AlphaVantageSerializers:
	records = LineChartRecordsSerializer()
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
