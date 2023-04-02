from dataclasses import dataclass

from core.chart.chart import Chart
from core.interval import Interval

@dataclass
class CandleStickChart(Chart):
	query_field_names = Chart.query_field_names + [ 'interval' ]
	data_field_names = Chart.data_field_names + [ 'open', 'high', 'low', 'close' ]
	volume_field_names = Chart.volume_field_names + [ 'volume_tick', 'volume_real' ]

	interval: Interval = None