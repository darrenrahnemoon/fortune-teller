from core.broker.broker import Broker
from typing import Literal
import numpy
import pandas
from dataclasses import dataclass

from core.chart import Chart, ChartGroup
from core.utils.logging import logging

from apps.next_period_high_low.config import NextPeriodHighLowStrategyConfig

logger = logging.getLogger(__name__)

@dataclass
class NextPeriodHighLowPrediction:
	chart: Chart = None
	high_percent_change: float = None
	low_percent_change: float = None
	broker: Broker = None

	@property
	def action(self):
		return 'buy' if abs(self.high_percent_change) > abs(self.low_percent_change) else 'sell'

	@property
	def sl(self):
		return self.low if self.action == 'buy' else self.high

	@property
	def tp(self):
		return self.high if self.action == 'buy' else self.low

	@property
	def last_price(self):
		return self.broker.get_last_price(self.chart.symbol)

	@property
	def high(self):
		return self.last_price * (self.high_percent_change + 1)

	@property
	def low(self):
		return self.last_price * (self.low_percent_change + 1)

@dataclass
class NextPeriodHighLowPreprocessorService:
	strategy_config: NextPeriodHighLowStrategyConfig = None

	def to_model_input(self, input_chart_group: ChartGroup):
		input_chart_group.dataframe = input_chart_group.dataframe.tail(self.strategy_config.backward_window_length)
		for chart in input_chart_group.charts:
			chart.data = chart.data.pct_change()
		input_chart_group.dataframe = input_chart_group.dataframe.fillna(0)
		# input_chart_group.dataframe = mean_normalize(dataframe)
		return input_chart_group.dataframe.to_numpy()

	def to_model_output(self, output_chart_group: ChartGroup):
		outputs = []
		output_chart_group.dataframe = output_chart_group.dataframe.fillna(method = 'ffill')
		for chart in output_chart_group.charts:
			high_pct_change = chart.data['high'].max() / chart.data['high'].iloc[0] - 1
			low_pct_change = chart.data['low'].min() / chart.data['low'].iloc[0] - 1
			outputs.append([
				0 if numpy.isnan(high_pct_change) else high_pct_change,
				0 if numpy.isnan(low_pct_change) else low_pct_change
			])
		return numpy.array(outputs)

	def from_model_output(self, outputs: numpy.ndarray):
		return [
			NextPeriodHighLowPrediction(
				chart = chart,
				high_percent_change = output[0],
				low_percent_change = output[1],
			)
			for chart, output in zip(self.strategy_config.output_chart_group.charts, outputs)
		]