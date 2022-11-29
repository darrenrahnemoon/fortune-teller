import typing
import pandas
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from core.broker import Broker
from core.utils.cls import instance_to_repr

class Position:
	def __init__(
		self,
		id = None,
		broker: 'Broker' = None,
		symbol: str = None,
		type: typing.Literal['long', 'short'] = None,
		size: int = None,
		entry_price: float = None,
		exit_price: float = None,
		open_timestamp: pandas.Timestamp = None,
		close_timestamp: pandas.Timestamp = None,
		tp: float = None,
		sl: float = None,
		order = None,
	):
		self.id = id
		self.broker = broker
		self.symbol = symbol
		self.type = type
		self.entry_price = entry_price
		self.open_timestamp = open_timestamp
		self.exit_price = exit_price
		self.close_timestamp = close_timestamp
		self.sl = sl
		self.tp = tp
		self.order = order
		self.size = size

	def __repr__(self) -> str:
		return instance_to_repr(self, [ 'id', 'type', 'symbol', 'size', 'sl', 'tp', 'status', 'open_timestamp', 'close_timestamp' ])

	def close(self):
		self.broker.close_position(self)
		return self

	@property
	def profit(self) -> float:
		exit_price = self.exit_price or self.broker.get_last_price(self.symbol)
		return self.size * (exit_price - self.entry_price)

	@property
	def loss(self) -> float:
		return self.profit * -1

	@property
	def profit_percentage(self) -> float:
		exit_price = self.exit_price or self.broker.get_last_price(self.symbol)
		return (exit_price / self.entry_price - 1) * 100

	@property
	def loss_percentage(self) -> float:
		return self.profit_percentage * -1

	@property
	def is_in_profit(self) -> bool:
		return self.profit > 0

	@property
	def is_in_loss(self) -> bool:
		return self.profit < 0

	@property
	def status(self):
		return 'closed' if self.exit_price else 'open'

	@property
	def duration(self) -> pandas.Timedelta:
		if not self.close_timestamp:
			return None
		return self.close_timestamp - self.open_timestamp