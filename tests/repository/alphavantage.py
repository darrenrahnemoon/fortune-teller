from core.repository import AlphaVantageRepository
from core.interval import Interval
from core.chart import LineChart
from core.utils.test import it, describe

@describe('AlphaVantageRepository')
def _():
	alphavantage_repository = AlphaVantageRepository()
	@it('should read economical data from AlphaVantageRepository')
	def _():
		chart = LineChart(
			symbol = 'TREASURY_YIELD',
			repository = alphavantage_repository,
			interval = Interval.Day(1),
			maturity = Interval.Year(30)
		).read()

		assert len(chart) != 0
		assert chart.data['value']['2022-10-28'] == 4.15

		dataframe = alphavantage_repository.read_chart(
			symbol = 'TREASURY_YIELD',
			interval = Interval.Day(1),
			maturity = Interval.Year(30)
		)
		assert dataframe.equals(chart.data)
