from pathlib import Path

from core.tensorflow.device.config import DeviceConfig
from core.tensorflow.dataset.config import DatasetConfig
from core.tensorflow.tuner.hyperband.config import HyperbandTunerConfig
from core.tensorflow.trainer.config import TrainerConfig
from core.tensorflow.tensorboard.config import TensorboardConfig

from core.interval import Interval
from core.chart import ChartGroup, CandleStickChart
from core.indicator import SeasonalityIndicator
from core.repository import Repository, SimulationRepository
from core.broker import Broker, SimulationBroker
from core.utils.config import Config, dataclass, field

@dataclass
class NextPeriodHighLowStrategyConfig(Config):
	interval: Interval = Interval.Minute(1)
	forward_window_length: Interval = Interval.Hour(3)
	backward_window_length: Interval = Interval.Day(2)

	metatrader_symbols: list[str] = field(
		default_factory = lambda: [
			'GBPUSD', 'AUDUSD', 'GBPJPY', 'EURUSD', 'EURCHF', 'EURGBP', 'EURJPY', 'GBPCHF', 'EURAUD', 'USDNOK', 'NZDJPY', 'AUDCAD', 'CADJPY', 'AUDNZD', 'AUDCHF', 'CADCHF', 'EURCAD', 'EURNZD', 'NZDCAD', 'SGDJPY', 'NZDCHF', 'GBPCAD', 'GBPAUD', 'USDSEK', 'GBPNZD', 'EURTRY', 'USDTRY', 'EURSEK', 'USDPLN', 'EURNOK'
		]
	)
	metatrader_broker: Broker = field(default_factory = SimulationBroker)
	
	alphavantage_repository: Repository = field(default_factory = SimulationRepository)

	def __post_init__(self) -> None:
		for field_name in [ 'forward_window_length', 'backward_window_length' ]:
			field = getattr(self, field_name)
			if isinstance(field, Interval):
				setattr(
					self,
					field_name,
					int(field.to_pandas_timedelta() // self.interval.to_pandas_timedelta())
				)

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
		chart_group.charts[0].attach_indicator(SeasonalityIndicator)
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
