from core.chart.chart import Chart

class TickChart(Chart):
	data_field_names = Chart.data_field_names + [ 'bid', 'ask', 'last' ]
	volume_field_names = Chart.volume_field_names + [ 'volume_tick', 'volume_real' ]
