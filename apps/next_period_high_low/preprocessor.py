from typing import Literal
import numpy
import pandas
from dataclasses import dataclass

from core.chart.group import ChartGroup
from core.utils.logging import logging

from apps.next_period_high_low.config import NextPeriodHighLowStrategyConfig

logger = logging.getLogger(__name__)

@dataclass
class NextPeriodHighLowPreprocessor:
	strategy_config: NextPeriodHighLowStrategyConfig = None

	def process_input(
		self,
		input_chart_group: ChartGroup,
		truncate_from: Literal['head', 'tail'] = 'head',
	):
		for chart in input_chart_group.charts:
			data: pandas.DataFrame = chart.data
			data = data.pct_change()
			chart.data = data
			chart.refresh_indicators()

		dataframe = input_chart_group.dataframe
		dataframe = dataframe.fillna(0)
		dataframe = getattr(dataframe, truncate_from)(self.strategy_config.backward_window_length + self.strategy_config.forward_window_length)
		if len(dataframe) < self.strategy_config.backward_window_length:
			pass # SHOULD DO: pad beginning of dataframe with zeros

		input_chart_group.dataframe = dataframe

	def to_model_input(self, input_chart_group: ChartGroup):
		dataframe = input_chart_group.dataframe
		# dataframe = mean_normalize(dataframe)
		return dataframe.to_numpy()

	def to_model_output(self, output_chart_group: ChartGroup):
		outputs = []
		for chart in output_chart_group.charts:
			outputs.append([
				chart.data['high'].max(),
				chart.data['low'].min()
			])
		return numpy.array(outputs)