import pandas
from dataclasses import dataclass, field

from apps.next_period_high_low.config import NextPeriodHighLowStrategyConfig
from core.chart import Symbol
from core.broker import Broker
from core.utils.time import now

@dataclass
class NextPeriodHighLowModelOutput:
	tp_change: float = None
	max_high_change: float = None
	min_low_change: float = None

@dataclass
class NextPeriodHighLowPrediction:
	strategy_config: NextPeriodHighLowStrategyConfig = field(repr = False)

	# Raw output
	model_output: NextPeriodHighLowModelOutput = None

	symbol: Symbol = None

	# Price Action
	action: str = field(default = None, init = False)
	tp: float = field(default = None, init = False)
	tp_change: float = field(default = None, init = False)
	sl: float = field(default = None, init = False)
	sl_change: float = field(default = None, init = False)

	# Additional Inferences
	max_high: float = field(default = None, init = False)
	min_low: float = field(default = None, init = False)

	# Current status of prices
	sell_price: float = field(default = None, init = False)
	buy_price: float = field(default = None, init = False)
	spread: float = field(default = None, init = False)
	spread_pips: float = field(default = None, init = False)

	broker: Broker = field(default = None, repr = False)
	timestamp: pandas.Timestamp = field(default_factory = now)

	def __post_init__(self):
		self.populate_prices()
		self.populate_model_inferences()
		self.populate_price_action()

	def populate_price_action(self):
		if self.model_output.tp_change > 0:
			self.action = 'buy'

			# Buy TP
			self.tp_change = self.model_output.max_high_change
			self.tp = self.sell_price * (self.tp_change + 1)
			self.tp -= self.spread

			# Buy SL
			self.sl_change = self.model_output.min_low_change
			self.sl = self.sell_price * (self.sl_change + 1)
			self.sl -= self.spread

		else:
			self.action = 'sell'

			# Sell TP
			self.tp_change = self.model_output.min_low_change
			self.tp = self.buy_price * (self.tp_change + 1)
			self.tp += self.spread

			# Sell SL
			self.sl_change = self.model_output.max_high_change
			self.sl = self.buy_price * (self.sl_change + 1)
			self.sl += self.spread

	def populate_model_inferences(self):
		self.max_high = self.sell_price * (self.model_output.max_high_change + 1)
		self.min_low = self.buy_price * (self.model_output.min_low_change + 1)

	def populate_prices(self):
		self.sell_price = self.broker.repository.get_last_price(
			symbol = self.symbol,
			intent = 'sell'
		)
		self.buy_price = self.broker.repository.get_last_price(
			symbol = self.symbol,
			intent = 'buy'
		)
		self.spread = abs(self.buy_price - self.sell_price)
		self.spread_pips = self.spread / self.broker.repository.get_pip_size(self.symbol)