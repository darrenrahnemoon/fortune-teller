from dataclasses import dataclass

from core.chart.chart import Chart
from core.interval import Interval

@dataclass
class LineChart(Chart):
	query_fields = Chart.query_fields + [ 'interval', 'maturity' ]
	data_fields = Chart.data_fields + [ 'value' ]

	interval: Interval = None
	maturity: Interval = None