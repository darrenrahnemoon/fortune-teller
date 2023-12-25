from core.trading.interval import Interval
from core.trading.chart import ChartGroup, CandleStickChart
from core.trading.indicator import SeasonalityIndicator
from core.trading.repository import Repository, SimulationRepository, MetaTraderRepository
from core.utils.config import Config, dataclass, field, on_stage

@dataclass
class AveMariaObservationConfig(Config):
	symbols: list[str] = field(
		default_factory = lambda: [
			'AUDCAD',
			'AUDCHF',
			'AUDJPY',
			'AUDNZD',
			'AUDUSD',
			'AUS200',
			'CADJPY',
			'CHFJPY',
			'EURAUD',
			'EURCAD',
			'EURCHF',
			'EURGBP',
			'EURJPY',
			'EURNOK',
			'EURNZD',
			'EURSEK',
			'EURUSD',
			'GBPAUD',
			'GBPCAD',
			'GBPCHF',
			'GBPJPY',
			'GBPNZD',
			'GBPUSD',
			'NATGAS',
			'NZDCAD',
			'NZDCHF',
			'NZDJPY',
			'NZDUSD',
			'SGDJPY',
			'UK100',
			'UKOIL',
			'US2000',
			'US30',
			'US500',
			'USDCAD',
			'USDCHF',
			'USDCNH',
			'USDHKD',
			'USDJPY',
			'USDMXN',
			'USDNOK',
			'USDSEK',
			'USDSGD',
			'USOIL',
			'XAGUSD',
			'XAUUSD',
		]
	)
	bars: int = 100
	intervals: list[Interval] = field(
		default_factory = lambda : [
			Interval.Minute(1),
			Interval.Minute(15),
			Interval.Minute(30),
			Interval.Hour(1),
			Interval.Hour(6),
			Interval.Hour(12),
			Interval.Day(1),
		]
	)

	repository: Repository = field(
		default_factory = lambda: on_stage(
			development = SimulationRepository,
			production = MetaTraderRepository,
		)()
	)

	def build_chart_group(self) -> dict[Interval, ChartGroup]:
		chart_groups = {
			interval : ChartGroup(
				name = 'AveMariaInputChartGroup',
				charts = [
					CandleStickChart(
						symbol = symbol,
						interval = interval,
						select = [ 'open', 'high', 'low', 'close' ],
						repository = self.repository,
					)
					for symbol in self.symbols
				]
			)
			for interval in self.intervals
		}
		# chart_groups[Interval.Minute(1)].charts[0].attach_indicator(SeasonalityIndicator, name = 'seasonality')
		return chart_groups