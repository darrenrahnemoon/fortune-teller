import numpy
from core.interval import Interval
from core.utils.test import describe, it

from apps.next_period_high_low.config import NextPeriodHighLowConfig
from apps.next_period_high_low.container import NextPeriodHighLowContainer
from apps.next_period_high_low.dataset import NextPeriodHighLowDataset

@describe('NextPeriodHighLowDataset')
def _():
	@it('should generate (x, y) pairs given an index')
	def _():
		config = NextPeriodHighLowConfig()
		config.strategy.backward_window_bars = 100
		config.strategy.forward_window_bars = 10
		config.strategy.metatrader_symbols = [ 'EURUSD', 'USDCAD', 'EURCAD' ]
		config.strategy.interval = Interval.Minute(1)

		container = NextPeriodHighLowContainer(config = config).price()
		sequence: NextPeriodHighLowDataset = container.sequence()

		assert sequence.common_time_window.from_timestamp < sequence.common_time_window.to_timestamp
		assert len(sequence) != 0

		expected_columns_count = sum([ len(chart.select) for chart in config.strategy.input_chart_group.charts ])
		expected_columns_count += len(config.strategy.input_chart_group.charts[0].indicators['seasonality'].value_fields)

		for index in range(5):
			x, y = sequence[index]
			assert x[-1] != y[0]
			assert x.shape == (100, expected_columns_count)
			assert not numpy.any(numpy.isnan(x))
			assert y.shape == (3, 2)
			assert not numpy.any(numpy.isnan(y))