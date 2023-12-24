from core.trading.repository import AlphaVantageRepository
from core.trading.interval import Interval
from core.trading.chart import LineChart
from core.utils.test import test

@test.group('AlphaVantageRepository')
def _():
	alphavantage_repository = AlphaVantageRepository()
	@test.case('should read economical data from AlphaVantageRepository')
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
