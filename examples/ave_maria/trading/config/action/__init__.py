from core.trading.interval import Interval
from core.trading.chart import ChartGroup, CandleStickChart
from core.trading.broker import Broker, SimulationBroker, MetaTraderBroker
from core.utils.config import Config, dataclass, field, on_stage
from .conditions import TradingConditions

@dataclass
class AveMariaActionConfig(Config):
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
			'EURNZD',
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
			'USDSGD',
			'USOIL',
			'XAGUSD',
			'XAUUSD',
		]
	)
	interval: Interval = Interval.Minute(15)
	bars: int = 4 * 24 * 6
	window_lengths: list[int] = field(
		default_factory = lambda: [
			4 * 24 * 1,
			4 * 24 * 2,
			4 * 24 * 3,
			4 * 24 * 4,
			4 * 24 * 5,
			4 * 24 * 6
		]
	)
	broker: Broker = field(
		default_factory = lambda : on_stage(
			development = SimulationBroker,
			production = MetaTraderBroker,
		)()
	)

	def build_chart_group(self):
		chart_group = ChartGroup(
			name = 'AveMariaOutputChartGroup',
			charts = [
				CandleStickChart(
					symbol = symbol,
					interval = self.interval,
					repository = self.broker.repository,
				)
				for symbol in self.symbols
			]
		)
		return chart_group
