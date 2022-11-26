from core.chart.chart import Chart
from core.interval import Interval

class LineChart(Chart):
	query_fields = Chart.query_fields + [ 'interval', 'maturity' ]
	value_fields = Chart.value_fields + [ 'value' ]

	def __init__(self, interval: Interval = None, **kwargs):
		self.interval = interval
		super().__init__(**kwargs)
