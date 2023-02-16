from core.size import Size

from core.broker import MetaTraderBroker
from core.order import Order
from core.utils.environment import is_windows
from core.utils.collection import is_any_of
from core.utils.test import describe, it

@describe('MetaTraderBroker', skip = not is_windows)
def _():
	broker = MetaTraderBroker()
	@it('should place orders and retrieve the placed order')
	def _():
		new_order = Order(
			broker = broker,
			type = 'sell',
			symbol = 'EURUSD',
			size = Size.Unit(1000),
			limit = 100, # EURUSD us never going to be $100 so order will be stuck in limit
		).place()
		assert new_order.id != None
		orders = broker.get_orders(symbol = new_order.symbol)
		assert is_any_of(orders, lambda existing_order: existing_order.id == new_order.id)
		
