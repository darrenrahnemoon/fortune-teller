from functools import cached_property
from dataclasses import dataclass, field

from core.chart import Symbol
from core.broker import Broker

def distance(a, b):
	return abs(a - b)

@dataclass
class NextPeriodHighLowPrediction:
	symbol: Symbol = None
	broker: Broker = field(default = None, repr = False)

	high_change: float = None
	low_change: float = None
	close_change: float = None

	@property
	def action(self):
		high_distance = distance(self.high_change, self.close_change)
		low_distance = distance(self.low_change, self.close_change)
		if high_distance > low_distance:
			return 'buy'
		return 'sell'

	@property
	def sl_change(self):
		return -2 * self.tp_change

	@property
	def tp_change(self):
		if self.action == 'buy':
			return (self.high_change + self.close_change) / 2
		return (self.low_change + self.close_change) / 2

	@property
	def tp(self):
		return self.last_price * (self.tp_change + 1)

	@property
	def sl(self):
		return self.last_price * (self.sl_change + 1)

	@cached_property
	def last_price(self):
		return self.broker.repository.get_last_price(
			symbol = self.symbol,
			intent = self.action,
		)

	@property
	def high(self):
		return self.last_price * (self.high_change + 1)

	@property
	def low(self):
		return self.last_price * (self.low_change + 1)