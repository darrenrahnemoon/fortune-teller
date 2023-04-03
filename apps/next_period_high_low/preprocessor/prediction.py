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

	broker: Broker = field(default = None, repr = False)
	timestamp: pandas.Timestamp = field(default_factory = now)
	reasons_to_not_trade: list = field(default_factory = list, init = False)

	@property
	def is_allowed_to_trade(self):
		return len(self.reasons_to_not_trade) == 0

	def __post_init__(self):
		self.populate_prices()
		self.populate_model_inferences()
		self.populate_price_action()
		self.populate_reasons_to_not_trade()

	def populate_reasons_to_not_trade(self):
		conditions = self.strategy_config.action.conditions

		# Inconclusive Action
		if self.action == None:
			self.reasons_to_not_trade.append('Inconclusive action.')

		# Weird model predictions / offsets
		if self.action == 'buy':
			if self.tp < self.buy_price:
				self.reasons_to_not_trade.append("TP less than buy price in a 'buy' order.")
			if self.sl > self.sell_price:
				self.reasons_to_not_trade.append("SL more than sell price in a 'buy' order.")
		if self.action == 'sell':
			if self.tp > self.buy_price:
				self.reasons_to_not_trade.append("TP more than buy price in a 'sell' order.")
			if self.sl < self.sell_price:
				self.reasons_to_not_trade.append("SL less than sell price in a 'sell' order.")

		# Spread
		spread_pips = self.spread / self.broker.repository.get_pip_size(self.symbol)
		if conditions.spread.min and conditions.spread.min > spread_pips:
			self.reasons_to_not_trade.append(f'Spread is less than {conditions.spread.min}: {spread_pips}')
		if conditions.spread.max and conditions.spread.max < spread_pips:
			self.reasons_to_not_trade.append(f'Spread is greater than {conditions.spread.max}: {spread_pips}')

		# TP Movement
		if conditions.tp_change.min and conditions.tp_change.min > abs(self.tp_change):
			self.reasons_to_not_trade.append(f'TP movement is less than {conditions.tp_change.min}: {abs(self.tp_change)}')
		if conditions.tp_change.max and conditions.tp_change.max < abs(self.tp_change):
			self.reasons_to_not_trade.append(f'TP movement is more than {conditions.tp_change.max}: {abs(self.tp_change)}')

		# DIFF SL / DIFF TP
		risk_over_reward = abs(self.sl_change) / abs(self.tp_change)
		if conditions.risk_over_reward.min and conditions.risk_over_reward.min > risk_over_reward:
			self.reasons_to_not_trade.append(f'Risk over reward is less than {conditions.risk_over_reward.min}: {risk_over_reward}')
		if conditions.risk_over_reward.max and conditions.risk_over_reward.max < risk_over_reward:
			self.reasons_to_not_trade.append(f'Risk over reward is more than {conditions.risk_over_reward.max}: {risk_over_reward}')

	def populate_price_action(self):
		if self.model_output.tp_change > 0:
			self.action = 'buy'

			# Buy TP
			self.tp_change = self.model_output.max_high_change
			self.tp_change -= self.strategy_config.action.conditions.model_output_adjustment_due_to_model_error
			self.tp = self.sell_price * (self.tp_change + 1)
			self.tp -= self.spread

			# Buy SL
			self.sl_change = self.model_output.min_low_change
			self.sl_change -= self.strategy_config.action.conditions.model_output_adjustment_due_to_model_error
			self.sl = self.sell_price * (self.sl_change + 1)
			self.sl -= self.spread
		elif self.model_output.tp_change < 0:
			self.action = 'sell'

			# Sell TP
			self.tp_change = self.model_output.min_low_change
			self.tp_change += self.strategy_config.action.conditions.model_output_adjustment_due_to_model_error
			self.tp = self.buy_price * (self.tp_change + 1)
			self.tp += self.spread

			# Sell SL
			self.sl_change = self.model_output.max_high_change
			self.sl_change += self.strategy_config.action.conditions.model_output_adjustment_due_to_model_error
			self.sl = self.buy_price * (self.sl_change + 1)
			self.sl += self.spread

	def populate_model_inferences(self):
		self.max_high = self.sell_price * (self.model_output.max_high_change + 1)
		self.min_low = self.buy_price * (self.model_output.min_low_change + 1)

	def populate_prices(self):
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