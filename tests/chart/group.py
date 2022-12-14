import pandas
from pymongo import common

from core.utils.test import it, describe
from core.interval import Interval
from core.chart import ChartGroup, CandleStickChart, LineChart
from core.broker import SimulationBroker

@describe('ChartGroup')
def _():
	@it('should read a group of charts and construct their values in a single dataframe')
	def _():
		broker = SimulationBroker()
		chart_group = ChartGroup(
			common_params={
				'broker': broker,
			}
		)
		chart_group.add_chart(CandleStickChart(symbol='USDCAD', interval=Interval.Minute(1)))
		chart_group.add_chart(CandleStickChart(symbol='EURUSD', interval=Interval.Minute(1)))
		chart_group.add_chart(LineChart(symbol='TREASURY_YIELD', interval=Interval.Day(1), maturity=Interval.Month(3)))
		chart_group.set_field('from_timestamp', pandas.Timestamp('2017-01-04'))
		chart_group.set_field('to_timestamp', pandas.Timestamp('2017-01-31'))
		chart_group.read()

		chart = chart_group.charts[1]
		assert chart.broker == None
		assert len(chart_group.dataframe.index) == len(chart.dataframe.index)
		assert len(chart_group.dataframe) != 0
		assert len(chart.data) != 0