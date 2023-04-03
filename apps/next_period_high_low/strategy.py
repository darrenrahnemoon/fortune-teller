import time
from dataclasses import dataclass

from core.strategy import Strategy
from core.order import Order
from core.size import Size
from core.tensorflow.tuner.base.service import TunerService
from core.utils.logging import Logger

from apps.next_period_high_low.trainer import NextPeriodHighLowTrainerService
from apps.next_period_high_low.predictor import NextPeriodHighLowPredictorService
from apps.next_period_high_low.config import NextPeriodHighLowStrategyConfig

logger = Logger(__name__)

@dataclass
class NextPeriodHighLowStrategy(Strategy):
	config: NextPeriodHighLowStrategyConfig = None

	trainer_service: NextPeriodHighLowTrainerService = None
	tuner_service: TunerService = None
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

			# Only one position per symbol
			positions = self.config.action.broker.get_positions(symbol = prediction.symbol, status = 'open')
			position = next((position for position in positions if position.symbol == prediction.symbol), None)
			if position:
				logger.info(f"Skipping due to an existing open position:\n{position}\n{prediction}")
				continue

			order = Order(
				type = prediction.action,
				symbol = prediction.symbol,
				tp = prediction.tp,
				sl = prediction.sl,
				size = Size.FixedAmountRiskManagement(1000),
				broker = self.config.action.broker,
			)
			order.place()

			if order.id:
				logger.info(f'Placed order:\n{order}\n{prediction}')
			else:
				logger.error(f'Failed to place an order:\n{order}\n{prediction}')
		time.sleep(60 * 5)
