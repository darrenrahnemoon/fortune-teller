from dataclasses import dataclass
from core.strategy import Strategy
from core.position import Position
from core.order import Order
from core.size import Size
from core.utils.logging import Logger

from apps.next_period_high_low.trainer import NextPeriodHighLowTrainerService
from apps.next_period_high_low.tuner import NextPeriodHighLowTunerService
from apps.next_period_high_low.predictor import NextPeriodHighLowPredictorService
from apps.next_period_high_low.preprocessor.prediction import NextPeriodHighLowPrediction
from apps.next_period_high_low.config import NextPeriodHighLowStrategyConfig

logger = Logger(__name__)

@dataclass
class NextPeriodHighLowStrategy(Strategy):
	config: NextPeriodHighLowStrategyConfig = None

	trainer_service: NextPeriodHighLowTrainerService = None
	tuner_service: NextPeriodHighLowTunerService = None
	predictor_service: NextPeriodHighLowPredictorService = None

	@property
	def conditions(self):
		return self.config.action.conditions

	def __post_init__(self):
		self.model = self.tuner_service.get_model(self.trainer_service.config.trial)
		self.trainer_service.load_weights(self.model)
		return super().__post_init__()

	def handler(self):
		predictions = self.predictor_service.predict(self.model, self.config.action.broker.now)
		for prediction in predictions:
			try:
				self.ensure_model_confidence_within_range(prediction)
				self.block_invalid_sl_tp(prediction)
				self.ensure_tp_change_within_range(prediction)
				positions = self.config.action.broker.get_positions(symbol = prediction.symbol, status = 'open')
				position = next(positions, None)
				if position:
					# self.block_running_losses(prediction, position)
					if position.type == prediction.action:
						self.modify_position(position, prediction)
						continue
					else:
						self.close_position(position, prediction)
				self.ensure_risk_over_reward_within_range(prediction)
				self.ensure_spread_within_range(prediction)
				self.ensure_only_one_open_order_at_a_time(prediction)
				self.place_order(prediction)
			except Exception as exception:
				logger.error(f'{exception}\n{prediction}')

	def ensure_only_one_open_order_at_a_time(self, prediction: NextPeriodHighLowPrediction):
		orders = self.config.action.broker.get_orders(symbol = prediction.symbol, status = 'open')
		order = next((order for order in orders if order.symbol == prediction.symbol), None)
		if order:
			raise Exception(f"An open Order already exists.\n{order}")

	def ensure_tp_change_within_range(self, prediction: NextPeriodHighLowPrediction):
		if self.conditions.tp_change.min and self.conditions.tp_change.min > abs(prediction.tp_change):
			raise Exception(f"Model calculated TP change '{prediction.tp_change}' is less than '{self.conditions.tp_change.min}'.")

		if self.conditions.tp_change.max and self.conditions.tp_change.max < abs(prediction.tp_change):
			raise Exception(f"Model calculated TP change '{prediction.tp_change}' is more than '{self.conditions.tp_change.max}'.")

	def ensure_model_confidence_within_range(self, prediction: NextPeriodHighLowPrediction):
		if self.conditions.model_confidence.min and self.conditions.model_confidence.min > abs(prediction.model_output.tp_change):
			raise Exception(f"Model predicted TP change confidence magnitude '{prediction.model_output.tp_change}' is less than '{self.conditions.model_confidence.min}'.")

		if self.conditions.model_confidence.max and self.conditions.model_confidence.max < abs(prediction.model_output.tp_change):
			raise Exception(f"Model predicted TP change confidence magnitude '{prediction.model_output.tp_change}' is more than '{self.conditions.model_confidence.max}'.")

	def ensure_risk_over_reward_within_range(self, prediction: NextPeriodHighLowPrediction):
		price = (prediction.buy_price + prediction.sell_price) / 2
		risk_over_reward = abs(prediction.sl - price) / abs(prediction.tp - price)

		if self.conditions.risk_over_reward.min and self.conditions.risk_over_reward.min > risk_over_reward:
			raise Exception(f"Trade risk over reward '{risk_over_reward}' is less than '{self.conditions.risk_over_reward.min}'.")

		if self.conditions.risk_over_reward.max and self.conditions.risk_over_reward.max < risk_over_reward:
			raise Exception(f"Trade risk over reward '{risk_over_reward}' is more than '{self.conditions.risk_over_reward.max}'.")

	def ensure_spread_within_range(self, prediction: NextPeriodHighLowPrediction):
		if self.conditions.spread_pips.min and self.conditions.spread_pips.min > prediction.spread_pips:
			raise Exception(f"Instrument spread pips '{prediction.spread_pips}' is less than '{self.conditions.spread_pips.min}'.")

		if self.conditions.spread_pips.max and self.conditions.spread_pips.max < prediction.spread_pips:
			raise Exception(f"Instrument spread pips '{prediction.spread_pips}' is more than '{self.conditions.spread_pips.max}'.")

	def block_invalid_sl_tp(self, prediction: NextPeriodHighLowPrediction):
		if prediction.action == 'buy':
			if prediction.tp < prediction.buy_price:
				raise Exception(f"Trade TP '{prediction.tp}' is less than buy price '{prediction.buy_price}' in a 'buy' order.")
			if prediction.sl > prediction.sell_price:
				raise Exception(f"Trade SL '{prediction.sl}' is more than sell price '{prediction.sell_price}' in a 'buy' order.")
		if prediction.action == 'sell':
			if prediction.tp > prediction.buy_price:
				raise Exception(f"Trade TP '{prediction.tp}' is more than buy price '{prediction.buy_price}' in a 'sell' order.")
			if prediction.sl < prediction.sell_price:
				raise Exception(f"Trade SL '{prediction.sl}' is less than sell price '{prediction.sell_price}' in a 'sell' order.")

	def block_running_losses(self, prediction: NextPeriodHighLowPrediction, position: Position):
		if position.type != prediction.action:
			return

		if position.type == 'buy' and position.sl > prediction.sl:
			raise Exception(f"Cannot let losses run. SL lowered from '{position.sl}' to '{prediction.sl}' in a 'buy' order.")

		if position.type == 'sell' and position.sl < prediction.sl:
			raise Exception(f"Cannot let losses run. SL increased from '{position.sl}' to '{prediction.sl}' in a 'sell' order.")

	def close_position(self, position: Position, prediction: NextPeriodHighLowPrediction):
		position.close()
		logger.info(f'Closed Position due to trend change.\n{position}\n{prediction}')

	def modify_position(self, position: Position, prediction: NextPeriodHighLowPrediction):
		old_sl = position.sl
		old_tp = position.tp
		position.sl = prediction.sl
		position.tp = prediction.tp
		position.save()
		logger.info(f'Modified Position.\nSL: {old_sl} -> {position.sl}\nTP: {old_tp} -> {position.tp}\n{position}{prediction}')

	def place_order(self, prediction: NextPeriodHighLowPrediction):
		order = Order(
			type = prediction.action,
			symbol = prediction.symbol,
			tp = prediction.tp,
			sl = prediction.sl,
			size = Size.FixedAmountRiskManagement(1000),
			broker = self.config.action.broker,
		)
		order.place()
		logger.info(f'Placed Order.\n{order}\n{prediction}')

	def run(self):
		logger.info(f'Observing Instruments:\n{self.config.observation.symbols}')
		logger.info(f'Trading Instruments:\n{self.config.action.symbols}')
		return super().run()