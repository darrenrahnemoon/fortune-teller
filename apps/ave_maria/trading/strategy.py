from dataclasses import dataclass
from core.trading.strategy import Strategy
from core.trading.position import Position
from core.trading.order import Order
from core.trading.size import Size
from core.utils.logging import Logger
from core.utils.config import FloatRangeConfig

from apps.ave_maria.tensorflow.trainer.service import AveMariaTrainerService
from apps.ave_maria.tensorflow.tuner.service import AveMariaTunerService
from apps.ave_maria.tensorflow.predictor.service import AveMariaPredictorService
from apps.ave_maria.tensorflow.preprocessor.prediction import AveMariaPrediction
from apps.ave_maria.trading.config import AveMariaTradingConfig

logger = Logger(__name__)

@dataclass
class AveMariaStrategy(Strategy):
	config: AveMariaTradingConfig = None

	trainer_service: AveMariaTrainerService = None
	tuner_service: AveMariaTunerService = None
	predictor_service: AveMariaPredictorService = None

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
				self.block_invalid_sl_tp(prediction)
				positions = self.config.action.broker.get_positions(symbol = prediction.symbol, status = 'open')
				position = next(positions, None)
				if position:
					self.ensure_tp_change_within_range(prediction, self.config.action.conditions.existing_position_tp_change)
					# self.block_running_losses(prediction, position)
					if position.type == prediction.action:
						self.modify_position(position, prediction)
						continue
					else:
						self.close_position(position, prediction)
				else:
					self.ensure_tp_change_within_range(prediction, self.config.action.conditions.new_order_tp_change)
				self.ensure_risk_over_reward_within_range(prediction)
				self.ensure_spread_within_range(prediction)
				self.ensure_only_one_open_order_at_a_time(prediction)
				self.place_order(prediction)
			except Exception as exception:
				logger.error(f'{exception}\n{prediction}')

	def ensure_only_one_open_order_at_a_time(self, prediction: AveMariaPrediction):
		orders = self.config.action.broker.get_orders(symbol = prediction.symbol, status = 'open')
		order = next((order for order in orders if order.symbol == prediction.symbol), None)
		if order:
			raise Exception(f"An open Order already exists.\n{order}")

	def ensure_tp_change_within_range(self, prediction: AveMariaPrediction, tp_change: FloatRangeConfig):
		if tp_change.min and tp_change.min > abs(prediction.tp_change):
			raise Exception(f"Model calculated TP change '{prediction.tp_change}' is less than '{tp_change.min}'.")

		if tp_change.max and tp_change.max < abs(prediction.tp_change):
			raise Exception(f"Model calculated TP change '{prediction.tp_change}' is more than '{tp_change.max}'.")

	def ensure_risk_over_reward_within_range(self, prediction: AveMariaPrediction):
		price = (prediction.buy_price + prediction.sell_price) / 2
		risk_over_reward = abs(prediction.sl - price) / abs(prediction.tp - price)

		if self.conditions.risk_over_reward.min and self.conditions.risk_over_reward.min > risk_over_reward:
			raise Exception(f"Trade risk over reward '{risk_over_reward}' is less than '{self.conditions.risk_over_reward.min}'.")

		if self.conditions.risk_over_reward.max and self.conditions.risk_over_reward.max < risk_over_reward:
			raise Exception(f"Trade risk over reward '{risk_over_reward}' is more than '{self.conditions.risk_over_reward.max}'.")

	def ensure_spread_within_range(self, prediction: AveMariaPrediction):
		if self.conditions.spread_pips.min and self.conditions.spread_pips.min > prediction.spread_pips:
			raise Exception(f"Instrument spread pips '{prediction.spread_pips}' is less than '{self.conditions.spread_pips.min}'.")

		if self.conditions.spread_pips.max and self.conditions.spread_pips.max < prediction.spread_pips:
			raise Exception(f"Instrument spread pips '{prediction.spread_pips}' is more than '{self.conditions.spread_pips.max}'.")

	def block_invalid_sl_tp(self, prediction: AveMariaPrediction):
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

	def block_running_losses(self, prediction: AveMariaPrediction, position: Position):
		if position.type != prediction.action:
			return

		if position.type == 'buy' and position.sl > prediction.sl:
			raise Exception(f"Cannot let losses run. SL lowered from '{position.sl}' to '{prediction.sl}' in a 'buy' order.")

		if position.type == 'sell' and position.sl < prediction.sl:
			raise Exception(f"Cannot let losses run. SL increased from '{position.sl}' to '{prediction.sl}' in a 'sell' order.")

	def close_position(self, position: Position, prediction: AveMariaPrediction):
		position.close()
		logger.info(f'Closed Position due to trend change.\n{position}\n{prediction}')

	def modify_position(self, position: Position, prediction: AveMariaPrediction):
		old_sl = position.sl
		old_tp = position.tp
		position.sl = prediction.sl
		position.tp = prediction.tp
		position.save()
		logger.info(f'Modified Position.\nSL: {old_sl} -> {position.sl}\nTP: {old_tp} -> {position.tp}\n{position}{prediction}')

	def place_order(self, prediction: AveMariaPrediction):
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