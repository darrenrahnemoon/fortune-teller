import numpy
from dataclasses import dataclass, field
from functools import cached_property

from core.broker.broker import Broker
from core.chart import ChartGroup, Symbol
from core.utils.logging import logging

from apps.next_period_high_low.config import NextPeriodHighLowStrategyConfig

logger = logging.getLogger(__name__)

@dataclass
class NextPeriodHighLowPrediction:
	symbol: Symbol = None
	high_percentage_change: float = None
	low_percentage_change: float = None
	broker: Broker = field(default = None, repr = False)

	@property
	def action(self):
		if abs(self.high_percentage_change) > abs(self.low_percentage_change):
			return 'buy'
		return 'sell'

	@property
	def sl(self):
		return self.last_price * (self.sl_percentage_change + 1)

	@property
	def tp(self):
		return self.last_price * (self.tp_percentage_change + 1)

	@property
	def sl_percentage_change(self):
		return self.tp_percentage_change * -1

	@property
	def tp_percentage_change(self):
		if abs(self.high_percentage_change) > abs(self.low_percentage_change):
			return self.high_percentage_change
		return self.low_percentage_change

	@cached_property
	def last_price(self):
		return self.broker.repository.get_last_price(
			symbol = self.symbol,
			intent = self.action,
		)

	@property
	def high(self):
		return self.last_price * (self.high_percentage_change + 1)

	@property
	def low(self):
		return self.last_price * (self.low_percentage_change + 1)

@dataclass
class NextPeriodHighLowPreprocessorService:
	strategy_config: NextPeriodHighLowStrategyConfig = None

	def to_model_input(self, input_chart_group: ChartGroup):
		input_chart_group.dataframe = input_chart_group.dataframe.tail(self.strategy_config.backward_window_length)
		for chart in input_chart_group.charts:
			chart.data = chart.data.pct_change()
		input_chart_group.dataframe = input_chart_group.dataframe.fillna(0)
		return input_chart_group.dataframe.to_numpy()

	def to_model_output(self, output_chart_group: ChartGroup):
		outputs = []
		output_chart_group.dataframe = output_chart_group.dataframe.fillna(method = 'ffill')
		for chart in output_chart_group.charts:
			# High
			max_high_index = chart.data['high'].idxmax()
			max_high = chart.data['high'].loc[max_high_index]
			current_high = chart.data['high'].iloc[0]
			if current_high == 0:
				high_pct_change = 0
			else:
				high_pct_change = max_high / current_high - 1
				if numpy.isnan(high_pct_change):
					high_pct_change = 0

			# Low
			min_low_index = chart.data['low'].idxmin()
			min_low = chart.data['low'].loc[min_low_index]
			current_low = chart.data['low'].iloc[0]
			if current_low == 0:
				low_pct_change = 0
			else:
				low_pct_change = min_low / current_low - 1
				if numpy.isnan(low_pct_change):
					low_pct_change = 0

			# Find out which end gets hit first
			action = 'sell' if min_low_index < max_high_index else 'buy'
			action = self.action_serializer.serialize(action)
			
			outputs.append([
				high_pct_change,
				low_pct_change
			])
		return numpy.array(outputs)

	def from_model_output(self, outputs: numpy.ndarray):
		return [
			NextPeriodHighLowPrediction(
				symbol = chart.symbol,
				high_percentage_change = output[0],
				low_percentage_change = output[1],
			)
			for chart, output in zip(self.strategy_config.output_chart_group.charts, outputs)
		]