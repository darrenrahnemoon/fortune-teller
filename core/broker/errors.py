from dataclasses import dataclass
from core.order import Order
from core.position import Position
from core.utils.error import Error

@dataclass
class OrderError(Error):
	order: Order = None

@dataclass
class PositionError(Error):
	position: Position = None