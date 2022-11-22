import logging

from lib.chart.chart import Chart
from lib.interval import Interval

logger = logging.getLogger(__name__)

class CandleStickChart(Chart):
	query_fields = Chart.query_fields + [ 'interval' ]
	value_fields = Chart.value_fields + [ 'open', 'high', 'low', 'close', 'spread', 'tick_volume', 'real_volume' ]

	def __init__(self, interval: Interval = None, **kwargs):
		self.interval = interval
		super().__init__(**kwargs)

	@property
	def interval(self):
		return self._interval

	@interval.setter
	def interval(self, value: Interval):
		if value and not isinstance(value, Interval):
			logger.error(f'Cannot process assigned interval. The chart will likely not be able to load any data: {value}')
		self._interval = value