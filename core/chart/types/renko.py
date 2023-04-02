from dataclasses import dataclass

from core.chart.chart import Chart

@dataclass
class RenkoChart(Chart):
	query_field_names = Chart.query_field_names + [ 'brick_size' ]
	data_field_names = Chart.data_field_names + [ 'open', 'high', 'low', 'close' ]

	brick_size: float = None