import pandas
from dataclasses import dataclass

from core.strategy import Strategy
from core.order import Order
from core.size import Size
from core.tensorflow.tuner.tuner.service import TunerService
from core.utils.collection import is_any_of
from apps.next_period_high_low.trainer import NextPeriodHighLowTrainerService
from apps.next_period_high_low.config import NextPeriodHighLowStrategyConfig

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
		orders = self.config.metatrader_broker.get_orders(status = 'open')
		positions = self.config.metatrader_broker.get_positions(status = 'open')

		for prediction in self.predict_prices(self.config.metatrader_broker.now):
			# Only one order per symbol
			if is_any_of(orders, lambda order: order.symbol == prediction['chart'].symbol):
				continue

			# Only one position per symbol
			if is_any_of(positions, lambda position: position.symbol == prediction['chart'].symbol):
				continue

			Order(
				type = prediction['action'],
				symbol = prediction['chart'].symbol,
				tp = prediction['tp'],
				sl = prediction['sl'],
				size = Size.RiskManagedPercentageOfBalance(0.01),
				broker = self.config.metatrader_broker,
			).place()

	def predict_changes(self, timestamp: pandas.Timestamp):
		predictions = self.trainer_service.predict(self.model, timestamp)
		for prediction in predictions:
			yield prediction

	def predict_prices(self, timestamp: pandas.Timestamp):
		predictions = self.predict_changes(timestamp)
		for prediction in predictions:
			prediction['last_price'] = self.config.metatrader_broker.get_last_price(
				symbol = prediction['chart'].symbol,
				timestamp = timestamp,
			)

			prediction['high'] = prediction['last_price'] * (prediction['high_pct_change'] + 1)
			prediction['low'] = prediction['last_price'] * (prediction['low_pct_change'] + 1)

			if abs(prediction['high_pct_change']) > abs(prediction['low_pct_change']):
				prediction['action'] = 'buy'
				prediction['tp'] = prediction['high']
				prediction['sl'] = prediction['low']
			else:
				prediction['action'] = 'sell'
				prediction['tp'] = prediction['low']
				prediction['sl'] = prediction['high']

			yield prediction

	def get_prediction_for_largest_change(self, timestamp: pandas.Timestamp):
		predictions = self.predict_prices(timestamp)

		def max_pct_change(prediction):
			return max(abs(prediction['high_pct_change']), abs(prediction['low_pct_change']))

		return max(predictions, key = max_pct_change)