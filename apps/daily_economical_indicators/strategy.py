import functools
from itertools import count
from keras_tuner.engine.hyperparameters import HyperParameters
import pandas
import keras
from dataclasses import dataclass

from pandas.core.indexes import interval

from core.broker import Broker, AlphaVantageBroker, SimulationBroker
from core.chart import ChartGroup, CandleStickChart
from core.indicator import SeasonalityIndicator
from core.strategy import Strategy
from core.interval import Interval

from .model import NextPeriodHighLowModel

@dataclass
class EconomicalStrategy(Strategy):
	# brokers used in the strategy
	alphavantage_broker: Broker = None
	metatrader_broker: Broker = None

	# Params
	trading_focus: CandleStickChart = None
	forward_window_size: int = 60 * 1
	backward_window_size: int = 60 * 24 * 1

	@property
	@functools.cache
	def chart_group_hash(self):
		return hash(repr(self.chart_group))

	def setup(self):
		self.chart_group = ChartGroup(
			charts = [
				CandleStickChart(
					symbol = symbol,
					interval = self.trading_focus.interval,
					broker = self.metatrader_broker,
					select = CandleStickChart.data_fields,
					count = self.backward_window_size
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

		self.model = NextPeriodHighLowModel(
			chart_group = self.chart_group,
			trading_focus = self.trading_focus,
			forward_window_size = self.forward_window_size,
			backward_window_size = self.backward_window_size
		)

	def train(self):
		print(self.model.build(HyperParameters()).summary()),

	def handler(self):
		self.chart_group.set_field('to_timestamp', self.metatrader_broker.now)
		self.chart_group.read()
		self.model.preprocess_input(
			chart_group = self.chart_group,
		)
		print(self.chart_group.dataframe)

broker = SimulationBroker()
broker.now = '2020-05-01'
strategy = EconomicalStrategy(
	alphavantage_broker=broker,
	metatrader_broker=broker,
	trading_focus=CandleStickChart(symbol='EURUSD', interval=Interval.Minute(1))
)
strategy.train()
strategy.handler()