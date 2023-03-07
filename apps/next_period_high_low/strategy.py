import time
import pandas
from dataclasses import dataclass

from core.strategy import Strategy
from core.order import Order
from core.size import Size
from core.tensorflow.tuner.tuner.service import TunerService
from core.utils.collection import is_any_of
from core.utils.logging import logging

from apps.next_period_high_low.preprocessor import NextPeriodHighLowPrediction
from apps.next_period_high_low.trainer import NextPeriodHighLowTrainerService
from apps.next_period_high_low.config import NextPeriodHighLowStrategyConfig

logger = logging.getLogger(__name__)

@dataclass
class NextPeriodHighLowStrategy(Strategy):
	config: NextPeriodHighLowStrategyConfig = None
	trainer_service: NextPeriodHighLowTrainerService = None
	tuner_service: TunerService = None

	def __post_init__(self):
		self.model = self.tuner_service.get_model(self.trainer_service.config.trial)
		self.trainer_service.load_weights(self.model)
		return super().__post_init__()

	def handler(self):
		predictions = self.get_predictions(self.config.metatrader_broker.now)
		for prediction in predictions:
			# Skip low movements
			if self.config.min_movement_percentage_to_trade:
				if abs(prediction.tp_percentage_change) < self.config.min_movement_percentage_to_trade:
					logger.debug(f"Skipping due to movement being less than '{self.config.min_movement_percentage_to_trade}': {prediction.high_percentage_change}%\n{prediction}")
					continue

			# Skip high spread instruments
			if self.config.max_spread_to_trade:
				spread = self.config.metatrader_broker.repository.get_spread(prediction.symbol)
				if spread > self.config.max_spread_to_trade:
					logger.debug(f"Skipping due to high spread: {spread}\n{prediction}")
					continue

			# if self.config.min_risk_over_reward_ratio_to_trade:
			# 	high_percent_change_magnitude = abs(prediction.high_percentage_change)
			# 	low_percent_change_magnitude = abs(prediction.low_percentage_change)
			# 	if prediction.action == 'buy':
			# 		risk_over_reward = high_percent_change_magnitude / low_percent_change_magnitude
			# 	else:
			# 		risk_over_reward = low_percent_change_magnitude / high_percent_change_magnitude
			# 	if risk_over_reward < self.config.min_risk_over_reward_ratio_to_trade:
			# 		logger.debug(f"Skipping due to R/R being less than '{self.config.min_risk_over_reward_ratio_to_trade}': {risk_over_reward}\n{prediction}")
			# 		continue

			if prediction.action == 'buy' and prediction.sl > prediction.last_price:
				logger.debug(f"Skipping 'buy' due to SL > last price: {prediction.sl} > {prediction.last_price}\n{prediction}")
				continue

			if prediction.action == 'sell' and prediction.sl < prediction.last_price:
				logger.debug(f"Skipping 'sell' due to SL < last price: {prediction.sl} < {prediction.last_price}\n{prediction}")
				continue

			# Only one order per symbol
			orders = self.config.metatrader_broker.get_orders(symbol = prediction.symbol, status = 'open')
			if is_any_of(orders, lambda order: order.symbol == prediction.symbol):
				logger.debug(f"Skipping due to an existing open order.\n{prediction}")
				continue

			# Only one position per symbol
			positions = self.config.metatrader_broker.get_positions(symbol = prediction.symbol, status = 'open')
			if is_any_of(positions, lambda position: position.symbol == prediction.symbol):
				logger.debug(f"Skipping due to an existing open position.\n{prediction}")
				continue

			Order(
				type = prediction.action,
				symbol = prediction.symbol,
				tp = prediction.tp,
				sl = prediction.sl,
				size = Size.Lot(0.01),
				broker = self.config.metatrader_broker,
			).place()
		time.sleep(60 * 15)

	def get_predictions(self, timestamp: pandas.Timestamp):
		predictions = self.trainer_service.predict(self.model, timestamp)
		for prediction in predictions:
			prediction.broker = self.config.metatrader_broker
			yield prediction

	def get_prediction_with_largest_change(self, timestamp: pandas.Timestamp):
		predictions = self.get_predictions(timestamp)

		def max_pct_change(prediction: NextPeriodHighLowPrediction):
			return max(abs(prediction.high_percentage_change), abs(prediction.low_percentage_change))

		return max(predictions, key = max_pct_change)