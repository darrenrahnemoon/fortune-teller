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
				if prediction.action == 'buy' and abs(prediction.high_percentage_change) < self.config.min_movement_percentage_to_trade:
					logger.debug(f"Skipping 'buy' of '{prediction.chart.symbol}' due to low movement: {prediction.high_percentage_change}%")
					continue
				if prediction.action == 'sell' and abs(prediction.low_percentage_change) < self.config.min_movement_percentage_to_trade:
					logger.debug(f"Skipping 'sell' of '{prediction.chart.symbol}' due to low movement: {prediction.low_percentage_change}%")
					continue

			# Skip high spread instruments
			if self.config.max_spread_to_trade:
				spread = self.config.metatrader_broker.repository.get_spread(prediction.chart.symbol)
				if spread > self.config.max_spread_to_trade:
					logger.debug(f"Skipping '{prediction.chart.symbol}' due to high spread: {spread}")
					continue

			# Only one order per symbol
			orders = self.config.metatrader_broker.get_orders(symbol = prediction.chart.symbol, status = 'open')
			if is_any_of(orders, lambda order: order.symbol == prediction.chart.symbol):
				logger.debug(f"Skipping '{prediction.chart.symbol}' due to an existing open order.")
				continue

			# Only one position per symbol
			positions = self.config.metatrader_broker.get_positions(symbol = prediction.chart.symbol, status = 'open')
			if is_any_of(positions, lambda position: position.symbol == prediction.chart.symbol):
				logger.debug(f"Skipping '{prediction.chart.symbol}' due to an existing open position.")
				continue

			if prediction.action == 'buy' and prediction.sl > prediction.last_price:
				logger.debug(f"Skipping 'buy' of '{prediction.chart.symbol}' due to SL > last price: {prediction.sl} > {prediction.last_price}")
				continue

			if prediction.action == 'sell' and prediction.sl < prediction.last_price:
				logger.debug(f"Skipping 'sell' of '{prediction.chart.symbol}' due to SL < last price: {prediction.sl} < {prediction.last_price}")
				continue

			sl_diff = abs(prediction.sl - prediction.last_price)
			tp_diff = abs(prediction.tp - prediction.last_price)
			if sl_diff > tp_diff:
				logger.debug(f"Skipping '{prediction.chart.symbol}' due to 'SL difference' > 'TP difference': {sl_diff} > {tp_diff}")
				continue

			# # Add the SL/TP offset percentage
			# sl_offset = self.config.sl_percentage_offset * prediction.last_price
			# tp_offset = self.config.tp_percentage_offset * prediction.last_price
			# if prediction.action == 'buy':
			# 	sl = prediction.sl - sl_offset
			# 	tp = prediction.tp - tp_offset
			# else:
			# 	sl = prediction.sl + sl_offset
			# 	tp = prediction.tp + tp_offset

			Order(
				type = prediction.action,
				symbol = prediction.chart.symbol,
				tp = prediction.tp,
				sl = prediction.sl,
				size = Size.PercentageOfBalanceRiskManagement(0.01),
				broker = self.config.metatrader_broker,
			).place()

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