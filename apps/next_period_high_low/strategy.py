from core.utils.time import TimestampLike
from functools import cache, partial
from dataclasses import dataclass

from core.strategy import Strategy
from core.tensorflow.tuner.tuner.service import TunerService
from apps.next_period_high_low.trainer import NextPeriodHighLowTrainerService
from apps.next_period_high_low.config import NextPeriodHighLowStrategyConfig

@dataclass
class NextPeriodHighLowStrategy(Strategy):
	config: NextPeriodHighLowStrategyConfig = None
	trainer: NextPeriodHighLowTrainerService = None
	tuner: TunerService = None

	def __post_init__(self):
		self.model = self.tuner.get_best_model()
		self.trainer.load_weights(self.model)
		return super().__post_init__()

	def predict_changes(self, timestamp: TimestampLike):
		return self.trainer.predict(self.model, timestamp)

	def predict_prices(self, timestamp: TimestampLike):
		predictions = self.predict_changes(timestamp)
		for prediction in predictions:
			prediction['from_price'] = self.config.metatrader_broker.get_last_price(prediction['chart'].symbol)
			prediction['high'] = prediction['from_price'] * (1 + prediction['high'])
			prediction['low'] = prediction['from_price'] * (1 + prediction['low'])
		return predictions

	def get_prediction_for_largest_change(self, timestamp: TimestampLike):
		predictions = self.predict_prices(timestamp)

		def get_max_diff(prediction):
			high_diff = abs(prediction['high'] - prediction['from_price'])
			low_diff = abs(prediction['low'] - prediction['from_price'])
			prediction['action'] = 'buy' if high_diff > low_diff else 'sell'
			return max(high_diff, low_diff)

		return max(predictions, key = get_max_diff)