from numpy import product
from core.utils.environment import stage
from dataclasses import dataclass, field
from typing import Any, TypedDict

@dataclass
class Config:
	pass

class EnvironmentSpecificValue(TypedDict):
	production: Any
	training: Any
	tuning: Any

def on_env(**kwargs: EnvironmentSpecificValue):
	if kwargs.get('training') == None:
		kwargs['training'] = kwargs.get('production')
	if kwargs.get('tuning') == None:
		kwargs['tuning'] = kwargs.get('training')

	def wrapper():
		value = kwargs.get(stage.get())
		return value()

	return wrapper