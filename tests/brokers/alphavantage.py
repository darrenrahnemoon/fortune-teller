from lib.interval import Interval
from lib.broker import AlphaVantageBroker
from lib.chart import LineChart
from lib.utils.test import it, describe

@describe('AlphaVantageBroker')
def _():
	alphavantage = AlphaVantageBroker()
	@it('should read economical data from AlphaVantageBroker')
	def _():
		chart = LineChart(
			symbol='TREASURY_YIELD',
			interval=Interval.Day(1),
			maturity=Interval.Year(30)
		).read_from(alphavantage)

		assert len(chart) != 0
		assert chart.data['2022-10-28'] == 4.15