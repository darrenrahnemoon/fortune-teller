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

	max_high_change: float = None
	max_high: float = None

	min_low_change: float = None
	min_low: float = None

	average_high_change: float = None
	average_high: float = None
 
	average_low_change: float = None
	average_low: float = None

	def __post_init__(self):
		self.max_high = self.last_price * (self.max_high_change + 1)
		self.average_high = self.last_price * (self.average_high_change + 1)

		self.min_low = self.last_price * (self.min_low_change + 1)
		self.average_low = self.last_price * (self.average_low_change + 1)

	@property
	def action(self):
		if self.average_high_change < 0 and self.average_low_change < 0:
			return 'sell'
		if self.average_high_change > 0 and self.average_low_change > 0:
			return 'buy'
		return

	@property
	def tp(self):
		if self.action == 'buy':
			return self.average_high
		return self.average_low

	@property
	def sl(self):
		if self.action == 'buy':
			return self.min_low * (1 - 0.00005)
		return self.max_high * (1 + 0.00005)

	@cached_property
	def last_price(self):
		return self.broker.repository.get_last_price(
			symbol = self.symbol,
			intent = self.action,
		)
