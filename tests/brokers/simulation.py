import pandas
from lib.chart import CandleStickChart, LineChart
from lib.broker import SimulationBroker, AlphaVantageBroker
from lib.interval import Interval

from lib.utils.test import it, describe

@describe('SimulationBroker')
def _():
	simulation = SimulationBroker()
	alphavantage = AlphaVantageBroker()

	@it('should read data from the database')
	def _():
		chart = CandleStickChart(
			symbol='EURUSD',
			interval=Interval.Minute(1),
			from_timestamp='2021-10',
			to_timestamp='2021-11',
		).read_from(simulation)

		assert len(chart) != 0
		assert chart.data.index.name == 'timestamp'
		for column in chart.value_fields:
			assert column in chart.data.columns, column

	@it("should upsert chart data to it's historical data")
	def _():
		chart = LineChart(symbol='INFLATION', interval=Interval.Year(1))

		simulation.remove_historical_data(chart)
		assert simulation.get_min_timestamp(chart) == None
		assert simulation.get_max_timestamp(chart) == None

		chart.read_from(alphavantage).write_to(simulation)

		assert simulation.get_min_timestamp(chart).date() == chart.data.index[0].date()
		assert simulation.get_max_timestamp(chart).date() == chart.data.index[-1].date()
