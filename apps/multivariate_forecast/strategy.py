import functools
from dataclasses import dataclass
from keras_tuner import HyperParameters

from core.broker import Broker, MetaTraderBroker, SimulationBroker
from core.chart import ChartGroup, CandleStickChart
from core.indicator import SeasonalityIndicator
from core.strategy import Strategy
from core.interval import Interval

from .model import NextPeriodHighLow

@dataclass
class MultivariateForecastStrategy(Strategy):
	# brokers used in the strategy
	alphavantage_broker: Broker = None
	metatrader_broker: Broker = None

	# Params
	interval: Interval = None
	forward_window_length: Interval or int = None
	backward_window_length: Interval or int = None

	def setup(self):
		if isinstance(self.forward_window_length, Interval):
			self.forward_window_length = self.forward_window_length.to_pandas_timedelta() // self.interval.to_pandas_timedelta()
		if isinstance(self.backward_window_length, Interval):
			self.backward_window_length = self.backward_window_length.to_pandas_timedelta() // self.interval.to_pandas_timedelta()
		self.model = NextPeriodHighLow(
			build_chart_group = self.build_chart_group,
			forward_window_length = self.forward_window_length,
			backward_window_length = self.backward_window_length,
		)

	def build_chart_group(self):
		chart_group = ChartGroup(
			charts = [
				CandleStickChart(
					symbol = symbol,
					interval = self.interval,
					broker = self.metatrader_broker,
					select = CandleStickChart.data_fields, # Only data fields for now
					count = self.backward_window_length
				)
				for symbol in [
					'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURNZD', 'EURUSD', 'EURAUD', 'EURTRY', 'EURNOK', 'EURSEK', 'EURCZK', 'EURDKK', 'EURHUF', 'EURPLN',
					'AUS200', 'CH20', 'EU50', 'FRA40', 'SING30', 'UK100', 'US100', 'US2000', 'US30', 'US500', 'NL25', 'CHINA50', 'INDIA50', 'ES35', 'GER30', 'JP225', 'TWIX',
					# 'AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'CHFJPY', 'SGDJPY', 'GBPCHF', 'GBPJPY', 'GBPAUD', 'GBPCAD', 'GBPNZD', 'NZDUSD', 'NZDCAD', 'NZDCHF', 'NZDJPY', 'USDCAD', 'USDCHF', 'USDJPY', 'USDSEK', 'USDDKK', 'USDNOK', 'USDSGD', 'USDZAR', 'USDHKD', 'USDMXN', 'USDTRY', 'USDPLN', 'USDCNH', 'USDCZK', 'USDHUF', 'XAUUSD', 'XAGUSD', 'NATGAS', 'UKOIL', 'USOIL', 'COPPER', 'HK50',
				]
			]
		)
		chart_group.charts[0].attach_indicator(SeasonalityIndicator)
		trading_focus = [ chart
			for chart in chart_group.charts
			if type(chart) == CandleStickChart
		]
		return chart_group, trading_focus

broker = SimulationBroker()
broker.now = '2020-05-01'
strategy = MultivariateForecastStrategy(
	alphavantage_broker=broker,
	metatrader_broker=broker,
	interval=Interval.Minute(1),
	forward_window_length=Interval.Hour(1),
	backward_window_length=Interval.Day(1)
)
strategy.model.cache_dataset()