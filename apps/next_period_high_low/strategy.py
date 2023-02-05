import pandas
from dataclasses import dataclass

from core.strategy import Strategy
from core.tensorflow.tuner.tuner.service import TunerService

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

	def predict_changes(self, timestamp: pandas.Timestamp):
		return self.trainer_service.predict(self.model, timestamp)

	def predict_prices(self, timestamp: pandas.Timestamp):
		predictions = self.predict_changes(timestamp)
		for prediction in predictions:
			prediction['last_price'] = self.config.metatrader_broker.get_last_price(
				symbol = prediction['chart'].symbol,
				timestamp = timestamp,
			)
			prediction['high'] = prediction['last_price'] * (prediction['high'] + 1)
			prediction['low'] = prediction['last_price'] * (prediction['low'] + 1)
		return predictions

	def get_prediction_for_largest_change(self, timestamp: pandas.Timestamp):
		predictions = self.predict_prices(timestamp)

		def get_max_diff(prediction):
			high_diff = abs(prediction['high'] - prediction['last_price'])
			low_diff = abs(prediction['low'] - prediction['last_price'])
			prediction['action'] = 'long' if high_diff > low_diff else 'short'
			return max(high_diff, low_diff)

		return max(predictions, key = get_max_diff)