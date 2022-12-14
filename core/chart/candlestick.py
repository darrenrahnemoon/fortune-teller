from dataclasses import dataclass

from core.chart.chart import Chart
from core.interval import Interval

@dataclass
class CandleStickChart(Chart):
	query_fields = Chart.query_fields + [ 'interval' ]
	data_fields = Chart.data_fields + [ 'open', 'high', 'low', 'close' ]
	volume_fields = Chart.volume_fields + [ 'tick_volume', 'real_volume' ]

	interval: Interval = None