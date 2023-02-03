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
	trainer_service: NextPeriodHighLowTrainerService = None
	tuner_service: TunerService = None

	def __post_init__(self):
		self.model = self.tuner_service.get_model(self.trainer_service.config.trial)
		self.trainer_service.load_weights(self.model)
		return super().__post_init__()

	def predict_changes(self, timestamp: TimestampLike):
		return self.trainer_service.predict(self.model, timestamp)

	def predict_prices(self, timestamp: TimestampLike):
		predictions = self.predict_changes(timestamp)
		for prediction in predictions:
			prediction['last_price'] = self.config.metatrader_broker.get_last_price(prediction['chart'].symbol)
			print('chart:', prediction['chart'].name)
			print('price:', prediction['last_price'])
			print('high:', prediction['high'])
			print('low:', prediction['low'], end='\n\n')
			prediction['high'] = prediction['last_price'] * prediction['high']
			prediction['low'] = prediction['last_price'] * prediction['low']
		return predictions

	def get_prediction_for_largest_change(self, timestamp: TimestampLike):
		predictions = self.predict_prices(timestamp)

		def get_max_diff(prediction):
			high_diff = abs(prediction['high'] - prediction['last_price'])
			low_diff = abs(prediction['low'] - prediction['last_price'])
			prediction['action'] = 'long' if high_diff > low_diff else 'short'
			return max(high_diff, low_diff)

		return max(predictions, key = get_max_diff)