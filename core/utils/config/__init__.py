import core.utils.environment as environment
from dataclasses import dataclass, field # intentionally imported `field``
from typing import Any, TypedDict

@dataclass
class Config:
	pass

@dataclass
class FloatRangeConfig(Config):
	min: float = None
	max: float = None

@dataclass
class IntRangeConfig(Config):
	min: int = None
	max: int = None

class StageSpecificValue(TypedDict):
	production: Any
	development: Any

def on_stage(**kwargs: StageSpecificValue):
	def wrapper():
		value = kwargs.get(environment.stage)
		return value()

	return wrapper