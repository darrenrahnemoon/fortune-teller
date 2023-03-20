import core.utils.environment as environment
from dataclasses import dataclass, field # intentionally imported `field``
from typing import Any, TypedDict

@dataclass
class Config:
	pass

class StageSpecificValue(TypedDict):
	production: Any
	development: Any

def on_environment(**kwargs: StageSpecificValue):
	def wrapper():
		value = kwargs.get(environment.stage)
		return value()

	return wrapper