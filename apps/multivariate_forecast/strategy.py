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
		if type(self.forward_window_length) == Interval:
			self.forward_window_length = self.forward_window_length.to_pandas_timedelta() // self.interval.to_pandas_timedelta()
		if type(self.backward_window_length) == Interval:
			self.backward_window_length = self.backward_window_length.to_pandas_timedelta() // self.interval.to_pandas_timedelta()

		self.chart_group = ChartGroup(
			charts = [
				CandleStickChart(
					symbol = symbol,
					interval = self.interval,
					broker = self.metatrader_broker,
					select = CandleStickChart.data_fields,
					count = self.backward_window_length
				)
				for symbol in [
					# 'AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD',
					# 'CADCHF', 'CADJPY',
					# 'CHFJPY',
					# 'SGDJPY',
					'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURNZD', 'EURUSD', 'EURAUD', 'EURTRY', 'EURNOK', 'EURSEK', 'EURCZK', 'EURDKK', 'EURHUF', 'EURPLN',
					# 'GBPCHF', 'GBPJPY', 'GBPAUD', 'GBPCAD', 'GBPNZD',
					# 'NZDUSD', 'NZDCAD', 'NZDCHF', 'NZDJPY',
					# 'USDCAD', 'USDCHF', 'USDJPY', 'USDSEK', 'USDDKK', 'USDNOK', 'USDSGD', 'USDZAR', 'USDHKD', 'USDMXN', 'USDTRY', 'USDPLN', 'USDCNH', 'USDCZK', 'USDHUF',
					# 'XAUUSD', 'XAGUSD',
					# 'NATGAS', 'UKOIL', 'USOIL',
					# 'COPPER',
					# 'HK50',
					'AUS200', 'CH20', 'EU50', 'FRA40', 'SING30', 'UK100', 'US100', 'US2000', 'US30', 'US500', 'NL25', 'CHINA50', 'INDIA50', 'ES35', 'GER30', 'JP225', 'TWIX',
				]
			]
		)

		# Add instrument-agnostic indicators to the first chart
		self.chart_group.charts[0].attach_indicator(SeasonalityIndicator)
		self.trading_focus = [
			chart
			for chart in self.chart_group.charts
			if type(chart) == CandleStickChart
		]

		self.model = NextPeriodHighLow(
			chart_group = self.chart_group,
			trading_focus = self.trading_focus,
			forward_window_length = self.forward_window_length,
			backward_window_length = self.backward_window_length,
		)

	def handler(self):
		self.chart_group.set_field('to_timestamp', self.metatrader_broker.now)
		self.chart_group.read()

broker = SimulationBroker()
broker.now = '2020-05-01'
strategy = MultivariateForecastStrategy(
	alphavantage_broker=broker,
	metatrader_broker=broker,
	interval=Interval.Minute(1),
	forward_window_length=Interval.Hour(1),
	backward_window_length=Interval.Day(1)
)
strategy.model.prepare_dataset()