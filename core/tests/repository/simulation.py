from core.chart import CandleStickChart, LineChart, Chart
from core.repository import SimulationRepository, AlphaVantageRepository
from core.interval import Interval

from core.utils.test import it, describe

@describe('SimulationRepository')
def _():
	simulation_repository = SimulationRepository()
	alphavantage_repository = AlphaVantageRepository()

	@describe('charts')
	def _():
		@it('should read chart data within the date range provided from the database')
		def _():
			chart = CandleStickChart(
				symbol = 'EURUSD',
				repository = simulation_repository,
				interval = Interval.Minute(1),
				from_timestamp = '2021-10',
				to_timestamp = '2021-11',
			).read()

			assert len(chart) != 0
			assert chart.data.index.name == Chart.timestamp_field
			assert chart.dataframe.index.min() >= chart.from_timestamp
			assert chart.dataframe.index.max() <= chart.to_timestamp
			for column in chart.value_fields:
				assert column in chart.data.columns, column
				assert chart.data[column].isna().all() == False

		@it('should read a specific number of bars from the database')
		def _():
			chart = CandleStickChart(
				symbol = 'EURUSD',
				repository = simulation_repository,
				interval = Interval.Minute(1),
				from_timestamp = '2021-10',
				count = 100
			).read()
			assert len(chart) == chart.count

		@it("should upsert chart data to it's historical data")
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