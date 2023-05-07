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
			'UK100', 'XAGUSD', 'UKOIL', 'US500', 'COPPER', 'USOIL', 'USDHKD', 'XAUUSD', 'US2000', 'US30', 'GBPNZD', 'USDCNH', 'USDSGD', 'SGDJPY', 'GBPAUD', 'USDMXN', 'USDCHF', 'GBPCAD', 'GBPCHF', 'NZDCAD', 'NZDUSD', 'EURNZD', 'CHFJPY', 'USDCAD', 'AUDUSD', 'GBPUSD', 'AUDCHF', 'AUDCAD', 'EURUSD', 'NZDJPY', 'EURCAD', 'USDJPY', 'AUDNZD', 'CADJPY', 'GBPJPY', 'EURGBP', 'EURAUD', 'AUDJPY', 'EURJPY'
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
