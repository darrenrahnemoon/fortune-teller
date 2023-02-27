import typing
import pandas
import typing
from dataclasses import dataclass

from core.chart import Symbol
if typing.TYPE_CHECKING:
	from core.broker import Broker
	from core.order import Order

PositionStatus = typing.Literal['open', 'closed']
PositionType = typing.Literal['buy', 'sell']

@dataclass
class Position:
	id: str or int = None
	broker: 'Broker' = None
	symbol: Symbol = None
	type: PositionType = None
	size: int = None
	entry_price: float = None
	exit_price: float = None
	open_timestamp: pandas.Timestamp = None
	close_timestamp: pandas.Timestamp = None
	tp: float = None
	sl: float = None
	status: PositionStatus = None
	order: 'Order' = None

	def close(self):
		self.broker.close_position(self)
		return self

	@property
	def profit(self) -> float:
		exit_price = self.exit_price or self.broker.repository.get_last_price(self.symbol)
		return self.size * (exit_price - self.entry_price)

	@property
	def loss(self) -> float:
		return self.profit * -1

	@property
	def profit_percentage(self) -> float:
		exit_price = self.exit_price or self.broker.repository.get_last_price(self.symbol)
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
	def duration(self) -> pandas.Timedelta:
		if (not self.close_timestamp) or (not self.open_timestamp):
			return None
		return self.close_timestamp - self.open_timestamp