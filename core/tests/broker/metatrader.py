from core.broker import MetaTraderBroker
from core.order import Order
from core.size import Size

from core.utils.environment import is_windows
from core.utils.collection import find, is_any_of
from core.utils.test import test

@test.group('MetaTraderBroker', skip = not is_windows)
def _():
	broker: MetaTraderBroker = None

	@test.before()
	def _():
		nonlocal broker
		broker = MetaTraderBroker()

	@test.case('should place a limit order retrieve the placed order and cancel it')
	def _():
		order = Order(
			broker = broker,
			type = 'sell',
			symbol = 'EURUSD',
			size = Size.Unit(1000),
			limit = 100, # EURUSD us never going to be $100 so order will be stuck in limit
			sl = 110,
			tp = 10,
		).place()

		assert type(order.id) == int
		orders = broker.get_orders(symbol = order.symbol)
		fetched_order = find(orders, lambda existing_order: existing_order.id == order.id)
		assert fetched_order
		assert fetched_order.sl == order.sl
		assert fetched_order.tp == order.tp

		order.cancel()
		orders = broker.get_orders(symbol = order.symbol)
		assert not is_any_of(orders, lambda existing_order: existing_order.id == order.id)

	@test.case('it should place a market order and get all the positions and cancel that executed market order')
	def _():
		order = Order(
			broker = broker,
			type = 'sell',
			symbol = 'EURUSD',
			size = Size.Unit(1000),
		).place()
		positions = broker.get_positions(symbol = order.symbol)
		position = find(positions, lambda position: position.order == order.id)

		assert position
		position.close()

		positions = broker.get_positions(symbol = order.symbol)