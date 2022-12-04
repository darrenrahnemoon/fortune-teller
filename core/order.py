import typing
import pandas
import typing 
from dataclasses import dataclass

if typing.TYPE_CHECKING:
	from core.broker import Broker
	from core.position import Position

from core.chart import Symbol
from core.size import Size

OrderStatus = typing.Literal['open', 'filled', 'cancelled']
OrderType = typing.Literal['long', 'short']

@dataclass
class Order:
	id: str or int = None
	broker: 'Broker' = None
	type: OrderType = None
	symbol: Symbol = None
	size: Size or int = None
	limit: float = None
	stop: float = None
	sl: float = None
	tp: float = None
	open_timestamp: pandas.Timestamp = None
	close_timestamp: pandas.Timestamp = None
	status: OrderStatus = None
	position: 'Position' = None

	def place(self, broker: 'Broker' = None):
		self.broker = broker or self.broker

		# Calculate size if size is a broker-dependant function
		if isinstance(self.size, Size):
			self.size = self.size.to_units(self)

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
		if (not self.close_timestamp) or (not self.open_timestamp):
			return None
		return self.close_timestamp - self.open_timestamp