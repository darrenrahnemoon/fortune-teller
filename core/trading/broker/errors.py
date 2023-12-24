from dataclasses import dataclass
from core.trading.order import Order
from core.trading.position import Position
from core.utils.error import Error

@dataclass
class OrderError(Error):
	order: Order = None

@dataclass
class PositionError(Error):
	position: Position = None