import numpy
import pandas
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
	broker: Broker = field(default = None, repr = False)

	high_percentage_change: float = None
	high_index: float = None

	low_percentage_change: float = None
	low_index: float = None

	@property
	def action(self):
		if self.high_index < self.low_index:
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
		if self.action == 'buy':
			return self.low_percentage_change
		return self.high_percentage_change

	@property
	def tp_percentage_change(self):
		if self.action == 'buy':
			return self.high_percentage_change
		return self.low_percentage_change

	@cached_property
	def last_price(self):
		return self.broker.repository.get_last_price(
			symbol = self.symbol,
			intent = self.action,
		)

@dataclass
class NextPeriodHighLowPreprocessorService:
	strategy_config: NextPeriodHighLowStrategyConfig = None

	def to_model_input(self, input_chart_group: ChartGroup):
		input_chart_group.dataframe = input_chart_group.dataframe.tail(self.strategy_config.backward_window_length)
		for chart in input_chart_group.charts:
			chart.data = chart.data.pct_change()
		input_chart_group.dataframe = input_chart_group.dataframe.fillna(0)
		return input_chart_group.dataframe.to_numpy()

	def get_inflection_point(
		self,
		series: pandas.Series,
		direction: 'max' or 'min',
	):
		inflection_index = getattr(series, f'idx{direction}')()
		inflection_value = series.loc[inflection_index]
		current_inflection_value = series.iloc[0]
		if current_inflection_value == 0:
			inflection_pct_change = 0
		else:
			inflection_pct_change = inflection_value / current_inflection_value - 1
			if numpy.isnan(inflection_pct_change):
				inflection_pct_change = 0
		return inflection_pct_change, inflection_index

	def to_model_output(self, output_chart_group: ChartGroup):
		outputs = []
		output_chart_group.dataframe = output_chart_group.dataframe.fillna(method = 'ffill')
		output_chart_group.dataframe = output_chart_group.dataframe.fillna(0)

		for chart in output_chart_group.charts:
			high_pct_change, high_index = self.get_inflection_point(chart.data['high'], 'max')
			low_pct_change, low_index = self.get_inflection_point(chart.data['low'], 'min')

			# Normalize indices
			current_index = chart.data.index[0]
			high_index = high_index.value - current_index.value
			low_index = low_index.value - current_index.value
			sum_index = high_index + low_index

			if sum_index == 0:
				high_index = 0
				low_index = 0
			else:
				high_index = high_index / sum_index
				low_index = low_index / sum_index

			outputs.append([
				[ high_pct_change, high_index ],
				[ low_pct_change, low_index ]
			])
		return numpy.array(outputs)

	def from_model_output(self, outputs: numpy.ndarray):
		return [
			NextPeriodHighLowPrediction(
				symbol = chart.symbol,
				high_percentage_change = output[0][0],
				high_index = output[0][1],
				low_percentage_change = output[1][0],
				low_index = output[1][1],
			)
			for chart, output in zip(self.strategy_config.output_chart_group.charts, outputs)
		]