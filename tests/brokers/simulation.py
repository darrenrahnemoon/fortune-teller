from core.chart import CandleStickChart, LineChart, Chart
from core.broker import SimulationBroker, AlphaVantageBroker
from core.strategy import Strategy
from core.order import Order
from core.interval import Interval
from core.size import Size

from core.utils.time import normalize_timestamp
from core.utils.test import it, describe

@describe('SimulationBroker')
def _():
	simulation_broker = SimulationBroker()
	alphavantage = AlphaVantageBroker()

	@describe('charts')
	def _():
		@it('should read chart data within the date range provided from the database')
		def _():
			chart = CandleStickChart(
				symbol='EURUSD',
				broker=simulation_broker,
				interval=Interval.Minute(1),
				from_timestamp='2021-10',
				to_timestamp='2021-11',
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
				symbol='EURUSD',
				broker=simulation_broker,
				interval=Interval.Minute(1),
				from_timestamp='2021-10',
				count=100
			).read()
			assert len(chart) == chart.count

		@it("should upsert chart data to it's historical data")
		def _():
			chart = LineChart(symbol='INFLATION', interval=Interval.Year(1), broker=alphavantage)

			simulation_broker.remove_historical_data(chart)
			assert simulation_broker.get_min_available_timestamp_for_chart(chart) == None
			assert simulation_broker.get_max_available_timestamp_for_chart(chart) == None
			chart.read()
			simulation_broker.write_chart(chart)

			assert simulation_broker.get_min_available_timestamp_for_chart(chart).date() == chart.data.index[0].date()
			assert simulation_broker.get_max_available_timestamp_for_chart(chart).date() == chart.data.index[-1].date()

	@describe('backtesting')
	def _():
		@it('should return the last price as of the current time of the broker')
		def _():
			simulation_broker.now = normalize_timestamp('2022-11-05')
			price = simulation_broker.get_last_price('EURUSD')
			assert price != None
			assert type(price) == float