from dataclasses import dataclass, field

from core.chart import Symbol
from core.broker import Broker

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

	last_price: float = None

	def __post_init__(self):
		self.max_high = self.last_price * (self.max_high_change + 1)
		self.average_high = self.last_price * (self.average_high_change + 1)

		self.min_low = self.last_price * (self.min_low_change + 1)
		self.average_low = self.last_price * (self.average_low_change + 1)

		# HACK: this should come after all other fields for `self.action`` to work
		self.last_price = self.broker.repository.get_last_price(
			symbol = self.symbol,
			intent = self.action,
		)

	@property
	def action(self):
		if self.average_high_change < 0 and self.average_low_change < 0:
			return 'sell'
		if self.average_high_change > 0 and self.average_low_change > 0:
			return 'buy'
		return

	@property
	def tp_change(self):
		if self.action == 'buy':
			return self.average_high_change
		return self.average_low_change

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
