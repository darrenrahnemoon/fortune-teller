import time
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

	def __post_init__(self):
		self.model = self.tuner_service.get_model(self.trainer_service.config.trial)
		self.trainer_service.load_weights(self.model)
		return super().__post_init__()

	def handler(self):
		predictions = self.predictor_service.predict(self.model, self.config.action.broker.now)
		for prediction in predictions:
			try:
				self.check_model_confidence(prediction)
				self.check_out_of_whack_predictions(prediction)
				self.check_minimum_tp_movement_to_trade(prediction)
				positions = self.config.action.broker.get_positions(symbol = prediction.symbol, status = 'open')
				position = next(positions, None)
				if position:
					if position.type == prediction.action:
						self.modify_position(position, prediction)
						continue
					else:
						self.close_position(position, prediction)
				self.check_risk_over_reward(prediction)
				self.check_spread(prediction)
				self.check_only_one_open_order_at_a_time(prediction)
				self.place_order(prediction)
			except Exception as exception:
				logger.error(f'{exception}\n{prediction}')
		time.sleep(60 * 2)

	def check_only_one_open_order_at_a_time(self, prediction: NextPeriodHighLowPrediction):
		orders = self.config.action.broker.get_orders(symbol = prediction.symbol, status = 'open')
		order = next((order for order in orders if order.symbol == prediction.symbol), None)
		if order:
			raise Exception(f"Skipping due to an existing open order:\n{order}")

	def check_minimum_tp_movement_to_trade(self, prediction: NextPeriodHighLowPrediction):
		min_tp_change = self.config.action.conditions.tp_change.min
		if min_tp_change and min_tp_change > abs(prediction.tp_change):
			raise Exception(f'TP movement is less than {min_tp_change}: {abs(prediction.tp_change)}')

		max_tp_change = self.config.action.conditions.tp_change.max
		if max_tp_change and max_tp_change < abs(prediction.tp_change):
			raise Exception(f'TP movement is more than {max_tp_change}: {abs(prediction.tp_change)}')

	def check_model_confidence(self, prediction: NextPeriodHighLowPrediction):
		min_tp_change = self.config.action.conditions.model_confidence.min
		if min_tp_change and min_tp_change > abs(prediction.model_output.tp_change):
			raise Exception(f'Model TP change confidence is less than {min_tp_change}: {abs(prediction.model_output.tp_change)}')

		max_tp_change = self.config.action.conditions.model_confidence.max
		if max_tp_change and max_tp_change < abs(prediction.model_output.tp_change):
			raise Exception(f'Model TP change confidence is more than {max_tp_change}: {abs(prediction.model_output.tp_change)}')

	def check_risk_over_reward(self, prediction: NextPeriodHighLowPrediction):
		price = (prediction.buy_price + prediction.sell_price) / 2 # Note this is naive but it'll do for now
		risk_over_reward = abs(prediction.sl - price) / abs(prediction.tp - price)

		min_risk_over_reward = self.config.action.conditions.risk_over_reward.min
		if min_risk_over_reward and min_risk_over_reward > risk_over_reward:
			raise Exception(f'Risk over reward is less than {min_risk_over_reward}: {risk_over_reward}')

		max_risk_over_reward = self.config.action.conditions.risk_over_reward.max
		if max_risk_over_reward and max_risk_over_reward < risk_over_reward:
			raise Exception(f'Risk over reward is more than {max_risk_over_reward}: {risk_over_reward}')

	def check_spread(self, prediction: NextPeriodHighLowPrediction):
		spread_pips = prediction.spread / prediction.broker.repository.get_pip_size(prediction.symbol)

		min_spread = self.config.action.conditions.spread.min
		if min_spread and min_spread > spread_pips:
			raise Exception(f'Spread is less than {min_spread}: {spread_pips}')

		max_spread = self.config.action.conditions.spread.max
		if max_spread and max_spread < spread_pips:
			raise Exception(f'Spread is greater than {max_spread}: {spread_pips}')

	def check_out_of_whack_predictions(self, prediction: NextPeriodHighLowPrediction):
		if prediction.action == 'buy':
			if prediction.tp < prediction.buy_price:
				raise Exception("TP less than buy price in a 'buy' order.")
			if prediction.sl > prediction.sell_price:
				raise Exception("SL more than sell price in a 'buy' order.")
		if prediction.action == 'sell':
			if prediction.tp > prediction.buy_price:
				raise Exception("TP more than buy price in a 'sell' order.")
			if prediction.sl < prediction.sell_price:
				raise Exception("SL less than sell price in a 'sell' order.")

	def close_position(self, position: Position, prediction: NextPeriodHighLowPrediction):
		position.close()
		logger.info(f'Closed Position due to trend change\n{position}\n{prediction}')


	def modify_position(self, position: Position, prediction: NextPeriodHighLowPrediction):
		old_sl = position.sl
		old_tp = position.tp
		position.sl = prediction.sl
		position.tp = prediction.tp
		position.save()
		logger.info(f'Modified Position:\nSL: {old_sl} -> {position.sl}\nTP: {old_tp} -> {position.tp}\n{position}{prediction}')

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
		logger.info(f'Placed order:\n{order}\n{prediction}')