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
class NextPeriodHighLowPreprocessorService:
	strategy_config: NextPeriodHighLowStrategyConfig = None

	def to_model_input(self, input_chart_group: ChartGroup):
		input_chart_group.dataframe = input_chart_group.dataframe.tail(self.strategy_config.backward_window_length)
		for chart in input_chart_group.charts:
			chart.data = chart.data.pct_change()
		input_chart_group.dataframe = input_chart_group.dataframe.fillna(0)
		return input_chart_group.dataframe.to_numpy()

	def to_model_output(self, output_chart_group: ChartGroup):
		pass

	def from_model_output(self, outputs: numpy.ndarray):
		pass