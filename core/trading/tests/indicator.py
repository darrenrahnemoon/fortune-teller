from core.trading.chart import CandleStickChart
from core.trading.indicator import MACDIndicator
from core.trading.repository import SimulationRepository

from core.trading.interval import Interval
from core.utils.test import test

@test.group('Indicator')
def _():
	simulation_repository = SimulationRepository()

	@test.case("should be able to attach to a chart before it's loaded")
	def _():
		chart = CandleStickChart(
			symbol = 'EURUSD',
			repository = simulation_repository,
			interval = Interval.Minute(1),
			from_timestamp = '2021-11',
			to_timestamp = '2021-12',
			indicators = {
				'macd': MACDIndicator(window_slow=10, window_fast=5)
			}
		).read()

		assert len(chart) != 0
		indicator = chart.indicators['macd']
		assert type(indicator) == MACDIndicator
		assert len(indicator) != 0

		chart.detach_indicator('macd')
		assert len(indicator) == 0

	@test.case("should be able to attach to a chart after a it's loaded")
	def _():
		chart = CandleStickChart(
			symbol = 'EURUSD',
			repository = simulation_repository,
			interval = Interval.Minute(1),
			from_timestamp = '2021-11',
			to_timestamp = '2021-12',
		).read()

		indicator = chart.attach_indicator(MACDIndicator(window_slow=10, window_fast=5))
		assert chart.indicators[MACDIndicator] != None
		assert chart.indicators[MACDIndicator] == indicator
		assert len(indicator) != 0

		chart.detach_indicator(MACDIndicator)
		assert len(indicator) == 0