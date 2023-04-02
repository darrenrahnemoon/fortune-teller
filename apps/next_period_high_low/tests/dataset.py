import numpy
from core.interval import Interval
from core.utils.test import describe, it

from apps.next_period_high_low.config import NextPeriodHighLowConfig
from apps.next_period_high_low.container import NextPeriodHighLowContainer
from apps.next_period_high_low.dataset.sequence import NextPeriodHighLowSequence

@describe('NextPeriodHighLowSequence')
def _():
	@it('should generate (x, y) pairs given an index')
	def _():
		config = NextPeriodHighLowConfig()
		config.strategy.backward_window_bars = 100
		config.strategy.forward_window_bars = 10
		config.strategy.metatrader_symbols = [ 'EURUSD', 'USDCAD', 'EURCAD' ]
		config.strategy.interval = Interval.Minute(1)

		container = NextPeriodHighLowContainer(config = config).price()
		sequence: NextPeriodHighLowSequence = container.sequence()

		assert sequence.common_time_window.from_timestamp < sequence.common_time_window.to_timestamp
		assert len(sequence) != 0

		input_chart_group = config.strategy.build_input_chart_group()
		expected_columns_count = sum(
			(
				len(chart.select) + sum(
					(
						len(indicator.value_fields)
						for indicator in chart.indicators
					)
				)
				for chart in input_chart_group.charts
			)
		)

		for index in range(5):
			x, y = sequence[index]
			assert x[-1] != y[0]
			assert x.shape == (100, expected_columns_count)
			assert not numpy.any(numpy.isnan(x))
			assert y.shape == (3, 2)
			assert not numpy.any(numpy.isnan(y))