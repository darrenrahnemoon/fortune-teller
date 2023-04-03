import pandas
from core.utils.config import Config, FloatRangeConfig, dataclass, field

@dataclass
class TradingConditions(Config):
	model_output_adjustment_due_to_model_error: float = 0.0004

	spread: FloatRangeConfig = field(
		default_factory = lambda: FloatRangeConfig(
			min = None,
			max = None,
		)
	)
	tp_change: FloatRangeConfig = field(
		default_factory = lambda: FloatRangeConfig(
			min = 0.0002,
			max = None,
		)
	)
	risk_over_reward: FloatRangeConfig = field(
		default_factory = lambda: FloatRangeConfig(
			min = 0.3,
			max = 2.5,
		)
	)

	def is_trading_hours(self, timestamp: pandas.Timestamp) -> bool:
		if timestamp.month == 1 and timestamp.day == 1:
			return False
		if timestamp.month == 12 and timestamp.day == 25:
			return False

		if timestamp.day_of_week == 4 and timestamp.hour > 22: # Friday at 10PM UTC market closes
			return False
		if timestamp.day_of_week == 5: # Saturday
			return False
		if timestamp.day_of_week == 6 and timestamp.hour < 22: # Monday at 10PM UTC market opens
			return False
		return True