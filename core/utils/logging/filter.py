from logging import Filter, LogRecord
from core.utils.collection import is_any_of

class MessageFilter(Filter):
	def __init__(self, values: list[str] = []) -> None:
		self.values = [ value.lower() for value in values ]

	def filter(self, record: LogRecord) -> bool:
		if len(self.values) == 0:
			return True

		message = record.getMessage()
		return is_any_of(self.values, lambda value: value in message.lower())
