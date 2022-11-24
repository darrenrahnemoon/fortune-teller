from lib.broker import SimulationBroker
from lib.chart import CandleStickChart
from lib.indicator import MACDIndicator

from lib.interval import Interval
from lib.utils.test import it, describe

@describe('Indicator')
def _():
	broker = SimulationBroker()

	@it("should be able to attach to a chart before it's loaded")
	def _():
		chart = CandleStickChart(
			symbol='EURUSD',
			interval=Interval.Minute(1),
			from_timestamp='2021-11',
			to_timestamp='2021-12',
			indicators={
				'macd': MACDIndicator(window_slow=10, window_fast=5)
			}
		).read(broker)

		assert len(chart) != 0
		indicator = chart.indicators['macd']
		assert type(indicator) == MACDIndicator
		assert len(indicator) != 0

		chart.remove_indicator('macd')
		assert len(indicator) == 0

	@it("should be able to attach to a chart after a it's loaded")
	def _():
		chart = CandleStickChart(
			symbol='EURUSD',
			interval=Interval.Minute(1),
			from_timestamp='2021-11',
			to_timestamp='2021-12',
		).read(broker)

		indicator = chart.add_indicator(MACDIndicator(window_slow=10, window_fast=5))
		assert chart.indicators[MACDIndicator] != None
		assert chart.indicators[MACDIndicator] == indicator
		assert len(indicator) != 0

		chart.remove_indicator(MACDIndicator)
		assert len(indicator) == 0