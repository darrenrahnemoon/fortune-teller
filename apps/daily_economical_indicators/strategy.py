from core.chart.chart import Chart
from core.strategy import Strategy
from core.chart import CandleStickChart, ChartGroup
from core.broker import SimulationBroker

broker = SimulationBroker()

class EconomicalStrategy(Strategy):
	def setup(self):

	def handler(self):
		group = ChartGroup(
			charts=[
				
			]
		)

