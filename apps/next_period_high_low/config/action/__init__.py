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
	interval: Interval = Interval.Hour(1)
	bars: int = 12
	broker: Broker = field(
		default_factory = on_stage(
			development = SimulationBroker,
			production = MetaTraderBroker,
		)
	)

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
