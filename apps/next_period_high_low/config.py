from pydantic import BaseSettings, Field

from core.interval import Interval
from core.chart import ChartGroup, CandleStickChart
from core.indicator import SeasonalityIndicator
from core.repository import Repository, SimulationRepository

class NextPeriodHighLowModelConfiguration(BaseSettings):
	validation_split: float = 0.3
	batch_size: int = 2
	epochs: int = 50
	steps_per_epoch: int = 20
	use_multiprocessing: bool = True
	max_queue_size: int = 10
	workers: int = 5
	use_device: str = 'CPU'
	hyperband_max_epochs: int = 10
	hyperband_reduction_factor: int = 3
	hyperband_iterations: int = 100

	repository: Repository = Field(default_factory = SimulationRepository)
	class Config:
		arbitrary_types_allowed = True

class NextPeriodHighLowConfiguration(BaseSettings):
	model: NextPeriodHighLowModelConfiguration = Field(
		default_factory = NextPeriodHighLowModelConfiguration
	)

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
					'AUDJPY', 'AUDUSD', 'CHFJPY', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY', 'AUDCAD', 'AUDCHF', 'AUDNZD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURNZD', 'GBPAUD', 'GBPCAD', 'NATGAS', 'NL25', 'NZDCAD', 'NZDCHF', 'NZDJPY', 'SGDJPY', 'TRYJPY', 'UK100', 'UKOIL', 'US2000', 'US30', 'US500', 'USDHKD', 'USDMXN', 'USDNOK', 'USDSEK', 'USDSGD', 'USDZAR', 'USOIL', 'XAGUSD', 'XAUUSD'
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