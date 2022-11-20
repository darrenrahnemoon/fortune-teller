from lib.chart.chart import Chart

class TickChart(Chart):
	value_fields = Chart.value_fields + [ 'bid', 'ask', 'last', 'tick_volume', 'real_volume' ]
