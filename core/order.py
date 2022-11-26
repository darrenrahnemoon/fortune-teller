import typing
import pandas
import typing 

if typing.TYPE_CHECKING:
	from core.broker import Broker
	from core.position import Position

class Order:
	def __init__(self,
		type: typing.Literal['long', 'short'] = None, 
		symbol: str = None,
		size: int or typing.Callable = None,
		limit: float = None,
		stop: float = None,
		sl: float = None,
		tp: float = None,
		open_timestamp: pandas.Timestamp = None,
		close_timestamp: pandas.Timestamp = None,
		status: typing.Literal['open', 'filled', 'closed', 'cancelled'] = None,
		id = None,
		broker: 'Broker' = None,
		position: 'Position' = None,
	) -> None:
		self.id = id
		self.broker = broker
		self.symbol = symbol
		self.type = type
		self.size = size
		self.open_timestamp = open_timestamp
		self.close_timestamp = close_timestamp
		self.limit = limit
		self.stop = stop
		self.sl = sl
		self.tp = tp
		self.position = position
		self.status = status

	def __repr__(self) -> str:
		return f"Order({', '.join([ f'{key}={repr(getattr(self, key))}' for key in [ 'id', 'type', 'symbol', 'size', 'limit', 'stop', 'sl', 'tp', 'status' ] if getattr(self, key) != None ])})"

	def place(self, broker: 'Broker' = None):
		self.broker = broker or self.broker

		# Calculate size if size is a broker-dependant function
		if callable(self.size):
			self.size = self.size(self)

		broker.place_order(self)
		return self

	def cancel(self):
		self.broker.cancel_order(self)
		return self

	@property
	def is_market_order(self):
		return self.limit == None and self.stop == None 

	@property
	def duration(self) -> pandas.Timedelta:
		if not self.close_timestamp:
			return None
		return self.close_timestamp - self.open_timestamp