from core.order import Order
from core.broker import SimulationBroker
from core.strategy import Strategy
from core.chart import CandleStickChart
from core.interval import Interval
from core.size import Size

from core.utils.test import describe, it

@describe('Strategy')
def _():
	@it('should backtest based on chart data')
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
					Order(type='long', symbol='EURUSD', size=Size.Lot(20)).place(self.broker)

				elif self.count == 5:
					positions = self.broker.get_positions('EURUSD', status='open')
					assert len(positions) == 1, 'Should have placed a market order in the next tick.'
					positions[-1].close()
					Order(type='long', symbol='EURUSD', size=Size.PercentageOfBalance(2), limit=10).place(self.broker)

				elif self.count == 10:
					orders = self.broker.get_orders('EURUSD')
					assert len(orders) == 2, 'Should show all orders'

					open_orders = self.broker.get_orders('EURUSD', status='open')
					assert len(open_orders) == 1, 'Should only show open orders'

					filled_orders = self.broker.get_orders('EURUSD', status='filled')
					assert len(filled_orders) == 1, 'Should only show filled orders'

					Order(type='long', symbol='EURUSD', size=Size.Lot(1)).place(self.broker)

				self.count += 1
		strategy = TestStrategy()
		strategy.broker = SimulationBroker()
		strategy.broker.timesteps = CandleStickChart(
			symbol='EURUSD',
			interval=Interval.Minute(1),
			from_timestamp='2021-05-13 12:00',
			to_timestamp='2021-05-13 14:10'
		)
		strategy.run()