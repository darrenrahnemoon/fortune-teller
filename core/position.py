import typing
import pandas
import typing
from dataclasses import dataclass

from core.chart import Symbol
from core.size import Size
if typing.TYPE_CHECKING:
	from core.broker import Broker
	from core.order import Order

PositionStatus = typing.Literal['open', 'closed']
PositionType = typing.Literal['buy', 'sell']

@dataclass
class Position:
	id: str or int = None
	symbol: Symbol = None
	type: PositionType = None
	size: Size = None
	status: PositionStatus = None
	open_timestamp: pandas.Timestamp = None
	entry_price: float = None
	close_timestamp: pandas.Timestamp = None
	exit_price: float = None
	tp: float = None
	sl: float = None
	order: 'Order' = None
	broker: 'Broker' = None

	def save(self):
		self.broker.modify_position(self)

	def close(self):
		self.broker.close_position(self)

	@property
	def profit(self) -> float:
		exit_price = self.exit_price or self.broker.repository.get_last_price(
			symbol = self.symbol,
			intent = 'sell' if self.type == 'buy' else 'buy'
		)
		return self.size.to_units * (exit_price - self.entry_price)

	@property
	def loss(self) -> float:
		return self.profit * -1

	@property
	def profit_percentage(self) -> float:
		exit_price = self.exit_price or self.broker.repository.get_last_price(
			symbol = self.symbol,
			intent = 'sell' if self.type == 'buy' else 'buy'
		)
		return (exit_price / self.entry_price - 1)

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
		if not self.open_timestamp:
			return None
		reference_timestamp = self.close_timestamp or self.broker.now
		return reference_timestamp - self.open_timestamp