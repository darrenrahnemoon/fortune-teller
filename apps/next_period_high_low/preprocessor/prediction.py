import pandas
from typing import Literal
from dataclasses import dataclass, field

from core.chart import Symbol
from core.broker import Broker
from core.utils.time import now

@dataclass
class NextPeriodHighLowPrediction:
	tp_change_action_threshold = 0

	symbol: Symbol = None
	action: str = field(default = None, init = False)
	tp: float = field(default = None, init = False)
	sl: float = field(default = None, init = False)

	max_high: float = field(default = None, init = False)
	min_low: float = field(default = None, init = False)

	broker: Broker = field(default = None, repr = False)
	timestamp: pandas.Timestamp = field(default_factory = now, repr = False)

	sell_price: float = field(default = None, init = False)
	buy_price: float = field(default = None, init = False)
	spread: float = field(default = None, init = False)

	max_high_change: float = None
	min_low_change: float = None
	tp_change: float = None
	sl_change: float = field(default = None, init = False)

	predicted_tp_change: float = None

	tp_timestamp: pandas.Timestamp = field(init = False)
	sl_timestamp: pandas.Timestamp = field(init = False)

	def __post_init__(self):
		self.sell_price = self.broker.repository.get_last_price(
			symbol = self.symbol,
			timestamp = self.timestamp,
			intent = 'sell'
		)
		self.buy_price = self.broker.repository.get_last_price(
			symbol = self.symbol,
			timestamp = self.timestamp,
			intent = 'buy'
		)
		self.spread = abs(self.buy_price - self.sell_price)

		self.max_high = self.sell_price * (self.max_high_change + 1)
		self.min_low = self.buy_price * (self.min_low_change + 1)

		self.predicted_tp_change = self.tp_change

		if self.tp_change > self.tp_change_action_threshold:
			self.action = 'buy'

			# Buy TP
			self.tp_change = self.max_high_change
			self.tp = self.sell_price * (self.tp_change + 1)
			self.tp -= self.spread

			# Buy SL
			self.sl_change = self.min_low_change
			self.sl = self.sell_price * (self.sl_change + 1)
			self.sl += self.spread
		elif self.tp_change < -1 * self.tp_change_action_threshold:
			self.action = 'sell'

			# Sell TP
			self.tp_change = self.min_low_change
			self.tp = self.buy_price * (self.tp_change + 1)
			self.tp += self.spread

			# Sell SL
			self.sl_change = self.max_high_change
			self.sl = self.buy_price * (self.sl_change + 1)
			self.sl += self.spread
