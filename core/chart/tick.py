from core.chart.chart import Chart

class TickChart(Chart):
	data_fields = [ 'bid', 'ask', 'last' ]
	volume_fields = [ 'tick_volume', 'real_volume' ]
