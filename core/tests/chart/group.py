from core.interval import Interval
from core.chart import ChartGroup, CandleStickChart, LineChart
from core.repository import SimulationRepository

from core.utils.test import test
from core.utils.time import normalize_timestamp

@test.group('ChartGroup')
def _():
	@test.case('should read a group of charts and block their values in a single dataframe')
	def _():
		simulation_repository = SimulationRepository()
		chart_group = ChartGroup(
			common_params = {
				'repository': simulation_repository,
				'from_timestamp': normalize_timestamp('2017-01-04'), # SHOULD DO: make chart fields normalize upon update
				'to_timestamp': normalize_timestamp('2017-01-31'),
			}
		)
		chart_group.add_chart(
			CandleStickChart(
				symbol = 'USDCAD', 
				interval = Interval.Minute(1)
			)
		)
		chart_group.add_chart(
			CandleStickChart(
				symbol = 'EURUSD', 
				interval = Interval.Minute(1)
			)
		)
		chart_group.add_chart(
			LineChart(
				symbol = 'TREASURY_YIELD', 
				interval = Interval.Day(1), 
				maturity = Interval.Month(3)
			)
		)
		chart_group.read()

		chart = chart_group.charts[1]
		assert len(chart_group.dataframe.index) == len(chart.dataframe.index)
		assert len(chart_group.dataframe) != 0
		assert len(chart.data) != 0