from core.chart.chart import Chart

class TickChart(Chart):
	data_fields = Chart.data_fields + [ 'bid', 'ask', 'last' ]
	volume_fields = Chart.volume_fields + [ 'volume_tick', 'volume_real' ]
