import pandas
from dataclasses import dataclass

from core.strategy import Strategy
from core.order import Order
from core.size import Size
from core.tensorflow.tuner.tuner.service import TunerService
from core.utils.collection import is_any_of

from apps.next_period_high_low.preprocessor import NextPeriodHighLowPrediction
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
		positions = self.config.metatrader_broker.get_positions(status = 'open')

		for prediction in self.get_predictions(self.config.metatrader_broker.now):
			orders = self.config.metatrader_broker.get_orders(symbol = prediction.chart.symbol, status = 'open')

			# Only one order per symbol
			if is_any_of(orders, lambda order: order.symbol == prediction.chart.symbol):
				continue

			positions = self.config.metatrader_broker.get_positions(symbol = prediction.chart.symbol, status = 'open')

			# Only one position per symbol
			if is_any_of(positions, lambda position: position.symbol == prediction.chart.symbol):
				continue

			Order(
				type = prediction.action,
				symbol = prediction.chart.symbol,
				tp = prediction.tp,
				sl = prediction.sl,
				size = Size.RiskManagedPercentageOfBalance(0.01),
				broker = self.config.metatrader_broker,
			).place()

	def get_predictions(self, timestamp: pandas.Timestamp):
		return self.trainer_service.predict(self.model, timestamp)

	def get_prediction_with_largest_change(self, timestamp: pandas.Timestamp):
		predictions = self.get_predictions(timestamp)

		def max_pct_change(prediction: NextPeriodHighLowPrediction):
			return max(abs(prediction.high_percent_change), abs(prediction.low_percent_change))

		return max(predictions, key = max_pct_change)