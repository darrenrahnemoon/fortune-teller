from core.interval import Interval
from core.chart import ChartGroup, CandleStickChart
from core.indicator import SeasonalityIndicator
from core.repository import Repository, SimulationRepository, MetaTraderRepository
from core.utils.config import Config, dataclass, field, on_stage

@dataclass
class ObservationConfig(Config):
	symbols: list[str] = field(
		default_factory = lambda: [
			'GBPNZD',
			'CADJPY',
			'EURAUD',
			'EURGBP',
			'GBPAUD',
			'GBPCAD',
			'AUDCAD',
			'AUDNZD',
			'AUDUSD',
			'EURCAD',
			'EURCHF',
			'EURJPY',
			'EURUSD',
			'GBPUSD',
			'USDCAD',
			'USDJPY',
			'AUDCHF',
			'AUDJPY',
			'CHFJPY',
			'GBPCHF',
			'GBPJPY',
			'NZDJPY',
			'SGDJPY',
			'USDCHF',
			'NZDUSD',
			'XAUUSD',
			'EURTRY',
			'EURNZD',
			'NZDCAD',
			'NZDCHF',
			'USDNOK',
			'USDSEK',
		]
	)
	interval: Interval = Interval.Minute(1)
	period: Interval = Interval.Day(2)
	repository: Repository = field(
		default_factory = on_stage(
			development = SimulationRepository,
			production = MetaTraderRepository,
		)
	)

	@property
	def bars(self) -> int:
		return int(self.period.to_pandas_timedelta() // self.interval.to_pandas_timedelta())

	def build_chart_group(self):
		chart_group = ChartGroup(
			name = 'NextPeriodHighLowInputChartGroup',
			charts = [
				CandleStickChart(
					symbol = symbol,
					interval = self.interval,
					select = CandleStickChart.data_field_names + [ 'volume_tick', 'spread_pips' ],
					repository = self.repository,
				)
				for symbol in self.symbols
			]
		)
		chart_group.charts[0].attach_indicator(SeasonalityIndicator, name = 'seasonality')
		return chart_group
