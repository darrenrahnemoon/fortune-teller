import numpy
from dataclasses import fields
from core.interval import Interval
from core.utils.test import test

from apps.pelosi_predictor.config import PelosiPredictorConfig
from apps.pelosi_predictor.container import PelosiPredictorContainer
from apps.pelosi_predictor.dataset.sequence import PelosiPredictorSequence

@test.group('PelosiPredictorSequence')
def _():
	@test.case('should generate (x, y) pairs given an index')
	def _():
		config = PelosiPredictorConfig()
		config.strategy.observation.interval = Interval.Minute(1)
		config.strategy.observation.bars = 100

		config.strategy.action.interval = Interval.Minute(1)
		config.strategy.action.bars = 10

		config.strategy.observation.symbols = [ 'EURUSD', 'USDCAD', 'EURCAD' ]
		config.strategy.action.symbols = [ 'EURUSD', 'USDCAD', 'EURCAD' ]

		container = PelosiPredictorContainer(config = config).model()
		sequence: PelosiPredictorSequence = container.sequence()

		assert sequence.common_time_window.from_timestamp < sequence.common_time_window.to_timestamp
		assert len(sequence) != 0

		input_chart_group = config.strategy.observation.build_chart_group()
		expected_columns_count = sum(
			(
				len(chart.select) + sum(
					(
						len(fields(indicator.Record))
						for indicator in chart.indicators.values()
					)
				)
				for chart in input_chart_group.charts
			)
		)

		for index in range(10):
			value = sequence[index]
			# When a specific item in the dataset is corrupted dataset returns None
			if value == None:
				continue
			x, y = value
			assert x[-1] != y[0]
			assert x.shape == (100, expected_columns_count), x.shape
			assert not numpy.any(numpy.isnan(x))
			assert y.shape == (3, 3), y.shape
			assert not numpy.any(numpy.isnan(y))