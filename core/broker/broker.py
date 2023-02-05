import pandas
from abc import abstractmethod, abstractproperty
from typing import TYPE_CHECKING, ClassVar
from dataclasses import dataclass

from core.order import Order, OrderStatus, OrderType
from core.position import Position, PositionStatus, PositionType
if TYPE_CHECKING:
	from core.chart import Symbol
	from core.repository import Repository

from core.utils.time import TimestampLike, now

@dataclass
class Broker:
	timezone: ClassVar[str] = 'UTC'
	repository: 'Repository' = None

	@property
	def now(self):
		return now(self.timezone)

	@abstractmethod
	def place_order(self, order: Order) -> Order:
		pass

	@abstractmethod
	def cancel_order(self, order: Order) -> Order:
		pass

	@abstractmethod
	def close_position(self, position: Position):
		pass

	@abstractmethod
	def get_last_price(
		self,
		symbol: 'Symbol',
		timestamp: pandas.Timestamp = None
	) -> float:
		pass

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
	def get_positions(
		self,
		symbol: 'Symbol' = None,
		type: PositionType = None,
		from_timestamp: TimestampLike = None,
		to_timestamp: TimestampLike = None,
		status: PositionStatus = None,
	) -> list[Position]:
		pass

	@abstractproperty
	def balance(self) -> float:
		pass

	@abstractproperty
	def equity(self) -> float:
		pass
