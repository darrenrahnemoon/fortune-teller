from dataclasses import fields
from core.trading.chart import CandleStickChart, LineChart, Chart
from core.trading.repository import SimulationRepository, AlphaVantageRepository
from core.trading.interval import Interval

from core.utils.test import test

@test.group('SimulationRepository')
def _():
	simulation_repository: SimulationRepository = None
	alphavantage_repository: SimulationRepository = None

	@test.before()
	def _():
		nonlocal simulation_repository
		nonlocal alphavantage_repository
		simulation_repository = SimulationRepository()
		alphavantage_repository = AlphaVantageRepository()

	@test.group('charts')
	def _():
		@test.case('should read chart data within the date range provided from the database')
		def _():
			chart = CandleStickChart(
				symbol = 'EURUSD',
				repository = simulation_repository,
				interval = Interval.Minute(1),
				from_timestamp = '2021-10',
				to_timestamp = '2021-11',
			).read()

			assert len(chart) != 0
			assert chart.data.index.name == 'timestamp'
			assert chart.dataframe.index.min() >= chart.from_timestamp
			assert chart.dataframe.index.max() <= chart.to_timestamp
			for field in fields(chart.Record):
				assert field.name in chart.data.columns, field.name
				assert chart.data[field.name].isna().all() == False

		@test.case('should read a specific number of bars from the database')
		def _():
			chart = CandleStickChart(
				symbol = 'EURUSD',
				repository = simulation_repository,
				interval = Interval.Minute(1),
				from_timestamp = '2021-10',
				count = 100
			).read()
			assert len(chart) == chart.count

		@test.case("should upsert chart data to it's historical data")
		def _():
			chart = LineChart(
				symbol = 'INFLATION',
				interval = Interval.Year(1),
				repository = alphavantage_repository
			)

			simulation_repository.remove_historical_data(chart)
			assert simulation_repository.get_min_available_timestamp(chart) == None
			assert simulation_repository.get_max_available_timestamp(chart) == None
			chart.read()
			simulation_repository.write_chart(chart)

			assert simulation_repository.get_min_available_timestamp(chart).date() == chart.data.index[0].date()
			assert simulation_repository.get_max_available_timestamp(chart).date() == chart.data.index[-1].date()
