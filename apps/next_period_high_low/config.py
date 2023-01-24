from pydantic import BaseSettings, Field

from core.tensorflow.device.config import DeviceConfig
from core.tensorflow.dataset.config import DatasetConfig
from core.tensorflow.tuner.hyperband.config import HyperbandTunerConfig
from core.tensorflow.training.config import TrainingConfig
from core.tensorflow.tensorboard.config import TensorboardConfig

from core.interval import Interval
from core.chart import ChartGroup, CandleStickChart
from core.indicator import SeasonalityIndicator
from core.repository import Repository, SimulationRepository

class NextPeriodHighLowStrategyConfig(BaseSettings):
	interval: Interval = Interval.Minute(1)
	forward_window_length: Interval = Interval.Minute(10)
	backward_window_length: Interval = Interval.Day(1)
	metatrader_repository: Repository = Field(default_factory = SimulationRepository)
	alphavantage_repository: Repository = Field(default_factory = SimulationRepository)

	def __init__(self, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)

		for field_name in [ 'forward_window_length', 'backward_window_length' ]:
			field = getattr(self, field_name)
			if isinstance(field, Interval):
				setattr(
					self,
					field_name,
					int(field.to_pandas_timedelta() // self.interval.to_pandas_timedelta())
				)

	def build_output_chart_group(self):
		chart_group = ChartGroup(
			name = 'NextPeriodHighLow',
			charts = [
				CandleStickChart(
					symbol = symbol,
					interval = self.interval,
					select = CandleStickChart.data_fields,
					count = self.backward_window_length,
					repository = self.metatrader_repository,
				)
				for symbol in [
					'GBPUSD', 'AUDUSD', 'GBPJPY', 'EURUSD', 'EURCHF', 'EURGBP', 'EURJPY', 'GBPCHF', 'EURAUD', 'USDNOK', 'NZDJPY', 'AUDCAD', 'CADJPY', 'AUDNZD', 'AUDCHF', 'CADCHF', 'EURCAD', 'EURNZD', 'NZDCAD', 'SGDJPY', 'NZDCHF', 'GBPCAD', 'GBPAUD', 'USDSEK', 'GBPNZD', 'EURTRY', 'USDTRY', 'EURSEK', 'USDPLN', 'EURNOK'
				]
			]
		)
		return chart_group

	def build_input_chart_group(self):
		chart_group = self.build_output_chart_group()
		chart_group.charts[0].attach_indicator(SeasonalityIndicator)
		return chart_group

	class Config:
		arbitrary_types_allowed = True

class NextPeriodHighLowConfig(BaseSettings):
	dataset: DatasetConfig = Field(default_factory = DatasetConfig)
	device: DeviceConfig = Field(default_factory = DeviceConfig)
	tensorboard: TensorboardConfig = Field(default_factory = TensorboardConfig)
	training: TrainingConfig = Field(default_factory = TrainingConfig)
	tuner: HyperbandTunerConfig = Field(default_factory = HyperbandTunerConfig)
	strategy: NextPeriodHighLowStrategyConfig = Field(default_factory = NextPeriodHighLowStrategyConfig)

	class Config:
		arbitrary_types_allowed = True