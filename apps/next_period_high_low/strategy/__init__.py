import pandas
from dataclasses import dataclass
import time

from core.strategy import Strategy
from core.order import Order
from core.size import Size
from core.tensorflow.tuner.tuner.service import TunerService
from core.utils.collection import is_any_of
from core.utils.logging import Logger

from apps.next_period_high_low.trainer.base import NextPeriodHighLowTrainerService
from apps.next_period_high_low.config import NextPeriodHighLowStrategyConfig
from .prediction import NextPeriodHighLowPrediction

logger = Logger(__name__)

@dataclass
class NextPeriodHighLowStrategy(Strategy):
	config: NextPeriodHighLowStrategyConfig = None
	price_trainer_service: NextPeriodHighLowTrainerService = None
	price_tuner_service: TunerService = None

	time_trainer_service: NextPeriodHighLowTrainerService = None
	time_tuner_service: TunerService = None

	def __post_init__(self):
		self.model = self.price_tuner_service.get_model(self.price_trainer_service.config.trial)
		self.price_trainer_service.load_weights(self.model)
		return super().__post_init__()

	def handler(self):
		predictions = self.get_predictions(self.config.metatrader_broker.now)
		for prediction in predictions:
			if prediction.action == None:
				logger.info(f'Skipping due to lack of certain action:\n{prediction}')
				continue
			# Skip low movements
			if self.config.min_movement_percentage_to_trade:
				if abs(prediction.tp_change) < self.config.min_movement_percentage_to_trade:
					logger.info(f"Skipping due to movement being less than '{self.config.min_movement_percentage_to_trade}': {prediction.tp_change}%\n{prediction}")
					continue

			# Skip high spread instruments
			if self.config.max_spread_to_trade:
				spread = self.config.metatrader_broker.repository.get_spread(prediction.symbol)
				if spread > self.config.max_spread_to_trade:
					logger.info(f"Skipping due to high spread: {spread}\n{prediction}")
					continue

			if prediction.action == 'buy' and prediction.sl > prediction.last_price:
				logger.info(f"Skipping 'buy' due to SL > last price: {prediction.sl} > {prediction.last_price}\n{prediction}")
				continue

			if prediction.action == 'sell' and prediction.sl < prediction.last_price:
				logger.info(f"Skipping 'sell' due to SL < last price: {prediction.sl} < {prediction.last_price}\n{prediction}")
				continue

			# Only one order per symbol
			orders = self.config.metatrader_broker.get_orders(symbol = prediction.symbol, status = 'open')
			if is_any_of(orders, lambda order: order.symbol == prediction.symbol):
				logger.info(f"Skipping due to an existing open order.\n{prediction}")
				continue

			# Only one position per symbol
			positions = self.config.metatrader_broker.get_positions(symbol = prediction.symbol, status = 'open')
			if is_any_of(positions, lambda position: position.symbol == prediction.symbol):
				logger.info(f"Skipping due to an existing open position.\n{prediction}")
				continue

			order = Order(
				type = prediction.action,
				symbol = prediction.symbol,
				tp = prediction.tp,
				sl = prediction.sl,
				size = Size.PercentageOfBalanceRiskManagement(0.005),
				broker = self.config.metatrader_broker,
			)
			order.place()
			logger.info(f'Sent Order:\n{order}\n{prediction}')
		time.sleep(60 * 5)

	def get_predictions(self, timestamp: pandas.Timestamp):
		predictions = self.price_trainer_service.predict(self.model, timestamp)
		for prediction in predictions:
			yield NextPeriodHighLowPrediction(
				symbol = prediction['symbol'],
				broker = self.config.metatrader_broker,
				max_high_change = prediction['max_high_change'],
				average_high_change = prediction['average_high_change'],
				min_low_change = prediction['min_low_change'],
				average_low_change = prediction['average_low_change']
			)
