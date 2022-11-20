from lib.chart.chart import Chart
class RenkoChart(Chart):
	query_fields = Chart.query_fields + [ 'brick_size' ] 
	value_fields = Chart.value_fields + [ 'open', 'high', 'low', 'close' ]

	def __init__(self,
		brick_size: float = None,
		**kwargs
	):
		self.brick_size = brick_size
		super().__init__(**kwargs)
