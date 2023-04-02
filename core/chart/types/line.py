from dataclasses import dataclass

from core.chart.chart import Chart
from core.interval import Interval

@dataclass
class LineChart(Chart):
	query_field_names = Chart.query_field_names + [ 'interval', 'maturity' ]
	data_field_names = Chart.data_field_names + [ 'value' ]

	interval: Interval = None
	maturity: Interval = None