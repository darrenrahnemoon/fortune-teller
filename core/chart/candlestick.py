from dataclasses import dataclass

from core.chart.chart import Chart
from core.interval import Interval

@dataclass
class CandleStickChart(Chart):
	query_fields = Chart.query_fields + [ 'interval' ]
	value_fields = Chart.value_fields + [ 'open', 'high', 'low', 'close', 'spread', 'tick_volume', 'real_volume' ]

	interval: Interval = None