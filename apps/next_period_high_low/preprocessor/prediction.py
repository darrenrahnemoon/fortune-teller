from dataclasses import dataclass, field
from functools import cached_property

from core.chart import Symbol
from core.broker import Broker

@dataclass
class NextPeriodHighLowPrediction:
	symbol: Symbol = None
	broker: Broker = field(default = None, repr = False)

	max_high_change: float = None
	max_high: float = field(default = None, init = False)

	min_low_change: float = None
	min_low: float = field(default = None, init = False)

	tp_change: float = None

	def __post_init__(self):
		self.max_high = self.last_price * (self.max_high_change + 1)
		self.min_low = self.last_price * (self.min_low_change + 1)

	@property
	def action(self):
		return 'buy' if self.tp_change > 0 else 'sell'

	@property
	def tp(self):
		return self.last_price * (self.tp_change + 1)

	@property
	def sl_change(self):
		if self.action == 'buy':
			return self.min_low_change - 0.0001
		return self.max_high_change + 0.0001

	@property
	def sl(self):
		return self.last_price * (self.sl_change + 1)

	@cached_property
	def last_price(self):
		return self.broker.repository.get_last_price(
			symbol = self.symbol,
			intent = self.action,
		)