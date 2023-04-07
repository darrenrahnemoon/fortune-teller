import time
from dataclasses import dataclass

from core.strategy import Strategy
from core.order import Order
from core.size import Size
from core.utils.logging import Logger
from core.broker.errors import OrderError, PositionError

from apps.next_period_high_low.trainer import NextPeriodHighLowTrainerService
from apps.next_period_high_low.tuner import NextPeriodHighLowTunerService
from apps.next_period_high_low.predictor import NextPeriodHighLowPredictorService
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
			# Prediction has a reason not to trade
			if not prediction.is_allowed_to_trade:
				logger.info(f'Skipping due to prediction having reasons not to trade:\n{prediction}')
				continue

			# Only one order per symbol
			orders = self.config.action.broker.get_orders(symbol = prediction.symbol, status = 'open')
			order = next((order for order in orders if order.symbol == prediction.symbol), None)
			if order:
				logger.info(f"Skipping due to an existing open order:\n{order}\n{prediction}")
				continue

			positions = self.config.action.broker.get_positions(symbol = prediction.symbol, status = 'open')
			position = next((position for position in positions if position.symbol == prediction.symbol), None)
			if position:
				# Prediction still believes the direction of the position is valid
				if position.type == prediction.action:
					# Readjust the SL/TPs to keep the gains going
					old_sl = position.sl
					old_tp = position.tp
					position.sl = prediction.sl
					position.tp = prediction.tp
					try:
						position.save()
						logger.info(f'Modified Position:\nSL: {old_sl} -> {position.sl}\nTP: {old_tp} -> {position.tp}\n{position}{prediction}')
					except PositionError as error:
						logger.error(f'Could not modify position at the request of prediction change:\n{error}\n{prediction}')
					continue
				# Prediction changed it's mind about the trend direction
				else:
					try:
						position.close()
						# Now place an order in the opposite direction below
					except PositionError as error:
						logger.error(f'Could not close position at the request of prediction direction change:\n{error}\n{prediction}')
						# Skip placing order as position likely wasn't closed
						continue
			try:
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
			except OrderError as error:
				logger.error(f'Failed to place order:\n{error}\n{prediction}')
		time.sleep(60 * 5)
