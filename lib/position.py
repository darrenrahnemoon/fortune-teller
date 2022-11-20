import pandas
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from lib.broker import Broker

class Position:
	def __init__(
		self,
		id = None,
		broker: 'Broker' = None,
		symbol: str = None,
		position_type: str = None,
		size: int = None,
		entry_price: float = None,
		entry_timestamp: pandas.Timestamp = None,
		exit_price: float = None,
		exit_timestamp: pandas.Timestamp = None,
		tp: float = None,
		sl: float = None,
		order = None,
	):
		self.id = id
		self.broker = broker
		self.symbol = symbol
		self.type = position_type
		self.entry_price = entry_price
		self.entry_timestamp = entry_timestamp
		self.exit_price = exit_price
		self.exit_timestamp = exit_timestamp
		self.sl = sl
		self.tp = tp
		self.order = order
		self.size = size

	def close(self):
		pass

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
	def status(self) -> bool:
		return 'closed' if self.exit_price else 'open'
