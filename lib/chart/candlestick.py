from lib.chart.chart import Chart
from lib.interval import Interval

class CandleStickChart(Chart):
	query_fields = Chart.query_fields + [ 'interval' ]
	value_fields = Chart.value_fields + [ 'open', 'high', 'low', 'close', 'spread', 'tick_volume', 'real_volume' ]

	def __init__(self, interval: Interval = None, **kwargs):
		self.interval = interval
		super().__init__(**kwargs)
