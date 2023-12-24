import pandas
from abc import abstractmethod, abstractproperty
from typing import TYPE_CHECKING, ClassVar
from dataclasses import dataclass

from core.trading.order import Order, OrderStatus, OrderType
from core.trading.position import Position, PositionStatus, PositionType
from core.trading.size import Size
if TYPE_CHECKING:
	from core.trading.chart import Symbol
	from core.trading.repository import Repository

from core.utils.time import TimestampLike, now

@dataclass
class Broker:
	timezone: ClassVar[str] = 'UTC'
	repository: 'Repository' = None

	@property
	def now(self):
		return now(self.timezone)

	@abstractmethod
	def get_orders(
		self,
		symbol: 'Symbol' = None,
		type: OrderType = None,
		from_timestamp: TimestampLike = None,
		to_timestamp: TimestampLike = None,
		status: OrderStatus = None,
	) -> list[Order]:
		pass

	@abstractmethod
	def place_order(self, order: Order, **kwargs) -> Order:
		pass

	@abstractmethod
	def cancel_order(self, order: Order) -> Order:
		pass

	@abstractmethod
	def get_positions(
		self,
		symbol: 'Symbol' = None,
		type: PositionType = None,
		from_timestamp: TimestampLike = None,
		to_timestamp: TimestampLike = None,
		status: PositionStatus = None,
	) -> list[Position]:
		pass

	@abstractmethod
	def modify_position(self, position: Position):
		pass

	@abstractmethod
	def close_position(self, position: Position):
		pass

	@abstractproperty
	def balance(self) -> float:
		pass

	@abstractproperty
	def equity(self) -> float:
		pass

	@abstractproperty
	def currency(self) -> str:
		pass

	@abstractmethod
	def get_units_in_one_lot(self, symbol: 'Symbol') -> int:
		pass
