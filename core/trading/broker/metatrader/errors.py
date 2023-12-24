import MetaTrader5
from typing import Any
from dataclasses import dataclass

from core.trading.broker.errors import (
	OrderError as BaseOrderError,
	PositionError as BasePositionError,
)

@dataclass
class MetaTraderError:
	request: Any = None
	response: Any = None
	last_error: Any = None

	def __post_init__(self, *args, **kwargs):
		super().__post_init__(*args, **kwargs)
		self.last_error = MetaTrader5.last_error()

@dataclass
class OrderError(MetaTraderError, BaseOrderError):
	pass

@dataclass
class PositionError(MetaTraderError, BasePositionError):
	pass
