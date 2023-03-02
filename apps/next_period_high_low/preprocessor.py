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
	model_prediction_error: float = 0.0005
	max_high_percentage_change: float = None
	min_high_percentage_change: float = None
	max_low_percentage_change: float = None
	min_low_percentage_change: float = None

	broker: Broker = field(default = None, repr = False)

	@property
	def action(self):
		if self.max_low_percentage_change > 0 \
			and self.min_high_percentage_change > 0 \
			and self.max_high_percentage_change > 0:
				return 'buy'

		if self.min_high_percentage_change < 0 \
			and self.max_low_percentage_change < 0 \
			and self.min_low_percentage_change < 0:
				return 'sell'

		return None

	@property
	def sl(self):
		return self.last_price * (self.sl_percentage_change + 1)

	@property
	def tp(self):
		return self.last_price * (self.tp_percentage_change + 1)

	@property
	def sl_percentage_change(self):
		if self.action == 'buy':
			return self.min_low_percentage_change - self.model_prediction_error
		if self.action == 'sell':
			return self.max_high_percentage_change + self.model_prediction_error
		return None

	@property
	def tp_percentage_change(self):
		if self.action == 'buy':
			return self.max_high_percentage_change
		if self.action == 'sell':
			return self.min_low_percentage_change
		return None

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

	def to_model_output(self, output_chart_group: ChartGroup):
		def ensure_not_nan(value):
			return 0 if numpy.isnan(value) else value

		outputs = []
		output_chart_group.dataframe = output_chart_group.dataframe.fillna(method = 'ffill')
		for chart in output_chart_group.charts:
			min_high_percentage_change = chart.data['high'].min() / chart.data['high'].iloc[0] - 1
			max_high_percentage_change = chart.data['high'].max() / chart.data['high'].iloc[0] - 1
			min_low_percentage_change = chart.data['low'].min() / chart.data['low'].iloc[0] - 1
			max_low_percentage_change = chart.data['low'].max() / chart.data['low'].iloc[0] - 1
			outputs.append([
				[ ensure_not_nan(max_high_percentage_change), ensure_not_nan(min_high_percentage_change) ],
				[ ensure_not_nan(max_low_percentage_change), ensure_not_nan(min_low_percentage_change) ]
			])
		return numpy.array(outputs)

	def from_model_output(self, outputs: numpy.ndarray):
		return [
			NextPeriodHighLowPrediction(
				symbol = chart.symbol,
				max_high_percentage_change = output[0][0],
				min_high_percentage_change = output[0][1],
				max_low_percentage_change = output[1][0],
				min_low_percentage_change = output[1][1],
			)
			for chart, output in zip(self.strategy_config.output_chart_group.charts, outputs)
		]