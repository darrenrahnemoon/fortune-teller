import pandas

from core.utils.test import it, describe
from core.interval import Interval
from core.chart import ChartGroup, CandleStickChart, LineChart
from core.broker import SimulationBroker

@describe('ChartGroup')
def _():
	@it('should read a group of charts and construct their values in a single dataframe')
	def _():
		broker = SimulationBroker()
		group = ChartGroup()
		group.add_chart(CandleStickChart(symbol='USDCAD', interval=Interval.Minute(1)))
		group.add_chart(CandleStickChart(symbol='EURUSD', interval=Interval.Minute(1)))
		group.add_chart(LineChart(symbol='TREASURY_YIELD', interval=Interval.Day(1), maturity=Interval.Month(3)))
		group.set_field('from_timestamp', pandas.Timestamp('2017-01-04'))
		group.set_field('to_timestamp', pandas.Timestamp('2017-01-31'))
		group.read(broker)

		chart = group.charts[1]
		assert chart.broker == None
		assert len(group.dataframe.index) == len(chart.dataframe.index)
		assert len(group.dataframe) != 0
		assert len(chart.data) != 0