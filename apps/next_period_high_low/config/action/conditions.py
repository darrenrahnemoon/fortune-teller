import pandas
from core.utils.config import Config, FloatRangeConfig, dataclass, field

@dataclass
class TradingConditions(Config):
	spread_pips: FloatRangeConfig = field(
		default_factory = lambda: FloatRangeConfig(
			min = None,
			max = 7,
		)
	)
	model_confidence: FloatRangeConfig = field(
		default_factory = lambda: FloatRangeConfig(
			min = None,
			max = None,
		)
	)
	tp_change: FloatRangeConfig = field(
		default_factory = lambda: FloatRangeConfig(
			min = 0.0007,
			max = None,
		)
	)
	risk_over_reward: FloatRangeConfig = field(
		default_factory = lambda: FloatRangeConfig(
			min = None,
			max = None,
		)
	)

	def is_trading_hours(self, timestamp: pandas.Timestamp) -> bool:
		if timestamp.tz:
			timestamp = timestamp.tz_convert('UTC')
		else:
			timestamp.tz_localize('UTC')
		# New Year
		if timestamp.month == 1 and timestamp.day == 1:
			return False

		# Christmas
		if timestamp.month == 12 and timestamp.day == 25:
			return False

		# Friday at 10PM UTC market closes
		if timestamp.day_of_week == 4 and timestamp.hour > 22: 
			return False

		# Saturday
		if timestamp.day_of_week == 5:
			return False

		# Monday at 10PM UTC market opens
		if timestamp.day_of_week == 6 and timestamp.hour < 22:
			return False

		return True