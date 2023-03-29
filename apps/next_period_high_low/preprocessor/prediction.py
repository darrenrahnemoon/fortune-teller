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
		self.sell_price = self.broker.repository.get_last_price(
			symbol = self.symbol,
			intent = 'sell',
		)
		self.buy_price = self.broker.repository.get_last_price(
			symbol = self.symbol,
			intent = 'buy',
		)
		self.max_high = self.buy_price * (self.max_high_change + 1)
		self.min_low = self.sell_price * (self.min_low_change + 1)

	@property
	def action(self):
		if self.tp_change > 0:
			return 'buy'
		return 'sell'

	@property
	def tp(self):
		if self.action == 'buy':
			return self.sell_price * (self.max_high_change + 1)
		return self.buy_price * (self.min_low_change + 1)

	@property
	def sl_change(self):
		if self.action == 'buy':
			return self.min_low_change
		return self.max_high_change

	@property
	def sl(self):
		if self.action == 'buy':
			return self.sell_price * (self.sl_change + 1)
		return self.buy_price * (self.sl_change + 1)
