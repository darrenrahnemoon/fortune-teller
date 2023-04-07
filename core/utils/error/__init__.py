from dataclasses import dataclass
from core.utils.cls.repr import pretty_repr

@dataclass
class Error(Exception):
	message: str

	def __post_init__(self):
		self.args = self.message, # tuple
	
	def __str__(self) -> str:
		return pretty_repr(self)