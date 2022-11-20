import pandas
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
	from lib.broker import Broker
	from lib.position import Position

class Order:
	def __init__(self,
		id = None,
		broker: 'Broker' = None,
		symbol: str = None,
		position_type: str = None, 
		size: int or Callable = None,
		limit: float = None,
		stop: float = None,
		sl: float = None,
		tp: float = None,
		open_timestamp: pandas.Timestamp = None,
		close_timestamp: pandas.Timestamp = None,
		status: str = None,
		position: 'Position' = None,
	) -> None:
		self.id = id
		self.broker = broker
		self.symbol = symbol
		self.type = position_type
		self.open_timestamp = open_timestamp
		self.close_timestamp = close_timestamp
		self.limit = limit
		self.stop = stop
		self.sl = sl
		self.tp = tp
		self.position = position
		self.status = status

		if type(size) == int:
			self.size = size
		elif callable(size):
			self.size = size(self)
		else:
			raise ValueError('Size must be either an integer indicating number of units or retrieved from Size.')

	def __repr__(self) -> str:
		return f'Order(size={self.size}, status={self.status}, limit={self.limit}, stop={self.stop}, sl={self.sl}, tp={self.tp})'

	def place(self):
		raise NotImplemented()

	def cancel(self):
		raise NotImplemented()

	@property
	def is_market_order(self):
		return self.limit == None and self.stop == None 