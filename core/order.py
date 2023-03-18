import typing
import pandas
import typing 
from dataclasses import dataclass

if typing.TYPE_CHECKING:
	from core.broker import Broker
	from core.position import Position

from core.chart import Symbol
from core.size import OrderDependantSize, Size

OrderStatus = typing.Literal['open', 'filled', 'cancelled']
OrderType = typing.Literal['buy', 'sell']

@dataclass
class Order:
	id: str or int = None
	broker: 'Broker' = None
	type: OrderType = None
	symbol: Symbol = None
	size: Size = None
	limit: float = None
	stop: float = None
	sl: float = None
	tp: float = None
	open_timestamp: pandas.Timestamp = None
	close_timestamp: pandas.Timestamp = None
	status: OrderStatus = None
	position: 'Position' = None

	def __post_init__(self):
		if isinstance(self.size, OrderDependantSize):
			self.size.order = self

	def place(self, broker: 'Broker' = None, **kwargs):
		self.broker = broker or self.broker
		self.broker.place_order(self, **kwargs)
		return self

	def cancel(self):
		self.broker.cancel_order(self)
		return self

	@property
	def is_market_order(self):
		return self.limit == None and self.stop == None

	@property
	def duration(self) -> pandas.Timedelta:
		if (not self.close_timestamp) or (not self.open_timestamp):
			return None
		return self.close_timestamp - self.open_timestamp