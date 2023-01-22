import numpy
from core.indicator import SeasonalityIndicator
from core.chart import ChartGroup, CandleStickChart
from core.repository import SimulationRepository
from core.interval import Interval
from core.utils.test import describe, it

from apps.next_period_high_low.model.preprocessor import NextPeriodHighLowPreprocessor
from apps.next_period_high_low.model.sequence import NextPeriodHighLowSequence

@describe('NextPeriodHighLowSequence')
def _():
	@it('should generate (x, y) pairs given an index')
	def _():
		backward_window_length = 100
		forward_window_length = 10
		sequence = NextPeriodHighLowSequence(
			backward_window_length = backward_window_length,
			forward_window_length = forward_window_length,
			build_input_chart_group = lambda: ChartGroup(
				charts = [
					CandleStickChart(
						symbol = 'EURUSD',
						interval = Interval.Minute(1),
						indicators = {
							'seasonality' : SeasonalityIndicator()
						}
					),
					CandleStickChart(
						symbol = 'USDCAD',
						interval = Interval.Minute(1)
					),
					CandleStickChart(
						symbol = 'EURCAD',
						interval = Interval.Minute(1)
					)
				]
			),
			build_output_chart_group = lambda: ChartGroup(
				charts = [
					CandleStickChart(
						symbol = 'USDCAD',
						interval = Interval.Minute(1)
					),
					CandleStickChart(
						symbol = 'EURCAD',
						interval = Interval.Minute(1)
					)
				]
			),
			repository = SimulationRepository(),
			preprocessor = NextPeriodHighLowPreprocessor(
				backward_window_length = backward_window_length,
				forward_window_length = forward_window_length
			)
		)
		assert sequence.common_time_window.from_timestamp < sequence.common_time_window.to_timestamp
		assert len(sequence) != 0
		input_chart_group = sequence.build_input_chart_group()
		expected_columns_count = sum([ len(chart.select) for chart in input_chart_group.charts ])
		expected_columns_count += len(input_chart_group.charts[0].indicators['seasonality'].value_fields)
		for i in range(5):
			x, y = sequence[i]
			assert x[-1] != y[0]
			assert x.shape == (100, expected_columns_count)
			assert not numpy.any(numpy.isnan(x))
			assert y.shape == (2, 2)
			assert not numpy.any(numpy.isnan(y))