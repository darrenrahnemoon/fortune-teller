import numpy
from dataclasses import dataclass

from core.order import Order
from core.broker import SimulationBroker, Broker
from core.strategy import Strategy
from core.chart import CandleStickChart
from core.interval import Interval
from core.size import Size
from core.repository import Repository
from core.utils.test import test

@test.group('SimulationBroker')
def _():
	broker: SimulationBroker = None

	@test.before_each()
	def _():
		nonlocal broker
		broker = SimulationBroker()

	@test.case('should backtest based on chart data')
	def _():
		@dataclass
		class TestStrategy(Strategy):
			broker: Broker = None
			repository: Repository = None

			def __post_init__(self):
				super().__post_init__()
				self.count = 0

			def handler(self):
				if self.count == 0:
					Order(
						type = 'buy',
						symbol = 'EURUSD',
						size = Size.Lot(20),
						broker = self.broker
					).place()

				elif self.count == 5:
					positions = self.broker.get_positions('EURUSD', status = 'open')
					assert len(positions) == 1, 'Should have placed a market order in the next tick.'
					positions[-1].close()
					Order(
						type = 'buy',
						symbol = 'EURUSD',
						size = Size.PercentageOfBalance(2),
						limit = 10,
						broker = self.broker
					).place()

				elif self.count == 10:
					orders = self.broker.get_orders('EURUSD')
					assert len(orders) == 2, 'Should show all orders'

					open_orders = self.broker.get_orders('EURUSD', status = 'open')
					assert len(open_orders) == 1, 'Should only show open orders'

					filled_orders = self.broker.get_orders('EURUSD', status = 'filled')
					assert len(filled_orders) == 1, 'Should only show filled orders'

					Order(
						type = 'buy',
						symbol = 'EURUSD',
						size = Size.Lot(1),
						broker = self.broker
					).place()

				self.count += 1
		strategy = TestStrategy(
			broker = broker,
			repository = broker.repository
		)
		broker.timesteps = CandleStickChart(
			symbol = 'EURUSD',
			interval = Interval.Minute(1),
			from_timestamp = '2021-05-13 12:00',
			to_timestamp = '2021-05-13 14:10'
		)
		broker.backtest(strategy)

	@test.case('should return the last price as of the current time of the repository')
	def _():
		broker.now = '2022-11-05'
		price = broker.repository.get_last_price('EURUSD')

		assert price != None
		assert type(price) == numpy.float64