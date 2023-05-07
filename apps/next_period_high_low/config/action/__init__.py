from core.interval import Interval
from core.chart import ChartGroup, CandleStickChart
from core.broker import Broker, SimulationBroker, MetaTraderBroker
from core.utils.config import Config, dataclass, field, on_stage
from .conditions import TradingConditions

@dataclass
class ActionConfig(Config):
	conditions: TradingConditions = field(default_factory = TradingConditions)
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
	period: Interval = Interval.Hour(12)
	broker: Broker = field(
		default_factory = on_stage(
			development = SimulationBroker,
			production = MetaTraderBroker,
		)
	)

	@property
	def bars(self) -> int:
		return int(self.period.to_pandas_timedelta() // self.interval.to_pandas_timedelta())

	def build_chart_group(self):
		chart_group = ChartGroup(
			name = 'NextPeriodHighLowOutputChartGroup',
			charts = [
				CandleStickChart(
					symbol = symbol,
					interval = self.interval,
					select = CandleStickChart.data_field_names,
					repository = self.broker.repository,
				)
				for symbol in self.symbols
			]
		)
		return chart_group
