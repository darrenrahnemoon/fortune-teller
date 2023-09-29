import pandas
from dataclasses import dataclass, field

from core.utils.serializer import MappingSerializer
from core.chart.serializers import ChartRecordsSerializer
from core.chart import CandleStickChart
from core.interval import Interval

interval_serializer = MappingSerializer({
	Interval.Minute(1) : '1min',
	Interval.Minute(5) : '5min',
	Interval.Minute(15) : '15min',
	Interval.Minute(30) : '30min',
	Interval.Hour(1) : '1hour',
	Interval.Hour(4) : '4hour',
})

@dataclass
class CandleStickChartSerializer(ChartRecordsSerializer):
	chart_class: type[CandleStickChart] = field(default_factory = lambda : CandleStickChart)

	def to_request(self, chart: CandleStickChart):
		return {
			'path' : f'/api/v3/historical-chart/{interval_serializer.serialize(chart.interval)}/{chart.symbol}',
			'params' : {
				'from' : chart.from_timestamp.strftime('%Y-%m-%d'),
				'to' : chart.to_timestamp.strftime('%Y-%m-%d'),
			}
		}

	def to_dataframe(self, records, *args, **kwargs):
		dataframe = pandas.DataFrame.from_records(records)
		dataframe = dataframe.rename(
			columns = {
				'date' : 'timestamp',
				'volume' : 'volume_real',
			}
		)
		return super().to_dataframe(dataframe, *args, **kwargs)
