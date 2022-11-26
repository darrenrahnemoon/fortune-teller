from core.interval import Interval
from core.broker import AlphaVantageBroker
from core.chart import LineChart
from core.utils.test import it, describe

@describe('AlphaVantageBroker')
def _():
	alphavantage = AlphaVantageBroker()
	@it('should read economical data from AlphaVantageBroker')
	def _():
		chart = LineChart(
			symbol='TREASURY_YIELD',
			interval=Interval.Day(1),
			maturity=Interval.Year(30)
		).read(alphavantage)

		assert len(chart) != 0
		assert chart.data['2022-10-28'] == 4.15