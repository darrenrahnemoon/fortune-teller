from core.chart import CandleStickChart, LineChart
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
		@it('should read chart data from the database')
		def _():
			chart = CandleStickChart(
				symbol='EURUSD',
				interval=Interval.Minute(1),
				from_timestamp='2021-10',
				to_timestamp='2021-11',
			).read(simulation_broker)

			assert len(chart) != 0
			assert chart.data.index.name == 'timestamp'
			for column in chart.value_fields:
				assert column in chart.data.columns, column

		@it("should upsert chart data to it's historical data")
		def _():
			chart = LineChart(symbol='INFLATION', interval=Interval.Year(1))

			simulation_broker.remove_historical_data(chart)
			assert simulation_broker.get_min_available_timestamp_for_chart(chart) == None
			assert simulation_broker.get_max_available_timestamp_for_chart(chart) == None

			chart.read(alphavantage).write(simulation_broker)

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

		@it('backtest based on chart data')
		def _():
			class TestStrategy(Strategy):
				def setup(self):
					self.count = 0

				def handler(self):
					hour_chart = CandleStickChart(
						symbol='EURUSD',
						interval=Interval.Hour(1),
						from_timestamp=self.broker.now - Interval.Hour(1).to_pandas_timedelta()
					).read(self.broker)

					minute_chart = CandleStickChart(
						symbol='EURUSD',
						interval=Interval.Minute(1),
						from_timestamp=self.broker.now - Interval.Hour(1).to_pandas_timedelta()
					).read(self.broker)

					assert hour_chart.data.iloc[-1]['high'] >= minute_chart.data.iloc[-1]['high']
					assert hour_chart.data.iloc[-1]['low'] <= minute_chart.data.iloc[-1]['low']
					assert hour_chart.data.iloc[-1].name.hour == minute_chart.data.iloc[-1].name.hour

					if self.count == 0:
						Order(type='long', symbol='EURUSD', size=Size.Lot(20)).place(simulation_broker)

					elif self.count == 5:
						positions = self.broker.get_positions('EURUSD', status='open')
						assert len(positions) == 1, 'Should have placed a market order in the next tick.'
						positions[-1].close()
						Order(type='long', symbol='EURUSD', size=Size.PercentageOfBalance(2), limit=10).place(simulation_broker)

					elif self.count == 10:
						orders = self.broker.get_orders('EURUSD')
						assert len(orders) == 2, 'Should show all orders'

						open_orders = self.broker.get_orders('EURUSD', status='open')
						assert len(open_orders) == 1, 'Should only show open orders'

						filled_orders = self.broker.get_orders('EURUSD', status='filled')
						assert len(filled_orders) == 1, 'Should only show filled orders'

						Order(type='long', symbol='EURUSD', size=Size.Lot(1)).place(simulation_broker)

					self.count += 1
			simulation_broker.add_strategy(TestStrategy)
			simulation_broker.backtest(
				timesteps=CandleStickChart(
					symbol='EURUSD',
					interval=Interval.Minute(1),
					from_timestamp='2021-05-15 12:00',
					to_timestamp='2021-05-15 14:10'
				)
			)