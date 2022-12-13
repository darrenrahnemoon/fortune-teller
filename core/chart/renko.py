from dataclasses import dataclass

from core.chart.chart import Chart

@dataclass
class RenkoChart(Chart):
	query_fields = Chart.query_fields + [ 'brick_size' ]
	data_fields = [ 'open', 'high', 'low', 'close' ]

	brick_size: float = None