from pathlib import Path
import pandas

from core.tensorflow.device.config import DeviceConfig
from core.tensorflow.dataset.config import DatasetConfig
from core.tensorflow.tuner.hyperband.config import HyperbandTunerConfig
from core.tensorflow.trainer.config import TrainerConfig
from core.tensorflow.tensorboard.config import TensorboardConfig

from core.interval import Interval
from core.chart import ChartGroup, CandleStickChart
from core.indicator import SeasonalityIndicator
from core.repository import Repository, SimulationRepository, AlphaVantageRepository
from core.broker import Broker, SimulationBroker, MetaTraderBroker
from core.utils.config import Config, dataclass, field, on_environment

@dataclass
class NextPeriodHighLowStrategyConfig(Config):
	interval: Interval = Interval.Minute(1)
	forward_window_length: Interval = Interval.Hour(3)
	backward_window_length: Interval = Interval.Day(2)

	metatrader_symbols: list[str] = field(
		default_factory = lambda: [
			'AUDUSD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'GBPCHF', 'GBPJPY', 'GBPUSD', 'EURAUD', 'AUDCAD', 'AUDCHF', 'AUDNZD', 'CADCHF', 'CADJPY', 'EURCAD', 'EURNZD', 'GBPAUD', 'GBPCAD', 'NZDCAD', 'NZDCHF', 'NZDJPY', 'SGDJPY', 'GBPNZD', 'US100'
		]
	)

	max_spread_to_trade: int = 50
	min_movement_percentage_to_trade: float = 0.0002
	min_risk_over_reward_ratio_to_trade: float = 1.5

	metatrader_broker: Broker = field(
		default_factory = on_environment(
			development = SimulationBroker,
			production = MetaTraderBroker,
		)
	)

	alphavantage_repository: Repository = field(
		default_factory = on_environment(
			development = SimulationRepository,
			production = AlphaVantageRepository,
		)
	)

	def __post_init__(self) -> None:
		for field_name in [ 'forward_window_length', 'backward_window_length' ]:
			field = getattr(self, field_name)
			if isinstance(field, Interval):
				setattr(
					self,
					field_name,
					int(field.to_pandas_timedelta() // self.interval.to_pandas_timedelta())
				)

	def is_trading_hours(self, timestamp: pandas.Timestamp) -> bool:
		if timestamp.day_of_week == 4 and timestamp.hour > 22: # Friday at 10PM UTC market closes
			return False
		if timestamp.day_of_week == 5: # Saturday
			return False
		if timestamp.day_of_week == 6 and timestamp.hour < 22: # Monday at 10PM UTC market opens
			return False
		return True

	@property
	def output_chart_group(self):
		chart_group = ChartGroup(
			name = 'NextPeriodHighLow',
			charts = [
				CandleStickChart(
					symbol = symbol,
					interval = self.interval,
					select = CandleStickChart.data_fields,
					count = self.backward_window_length,
					repository = self.metatrader_broker.repository,
				)
				for symbol in self.metatrader_symbols
			]
		)
		return chart_group

	@property
	def input_chart_group(self):
		chart_group = self.output_chart_group
		chart_group.charts[0].attach_indicator(SeasonalityIndicator, name = 'seasonality')
		return chart_group

@dataclass
class NextPeriodHighLowConfig(Config):
	dataset: DatasetConfig = field(default_factory = DatasetConfig)
	device: DeviceConfig = field(default_factory = DeviceConfig)
	tensorboard: TensorboardConfig = field(default_factory = TensorboardConfig)
	trainer: TrainerConfig = field(default_factory = TrainerConfig)
	tuner: HyperbandTunerConfig = field(default_factory = HyperbandTunerConfig)
	strategy: NextPeriodHighLowStrategyConfig = field(default_factory = NextPeriodHighLowStrategyConfig)
	artifacts_directory: Path = Path('./apps/next_period_high_low/artifacts')