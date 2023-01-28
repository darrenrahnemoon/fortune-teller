from typing import Literal
import numpy
import pandas
from dataclasses import dataclass

from core.chart import Chart, ChartGroup
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
		truncate_len: int = 0,
	):
		if truncate_len == 0:
			truncate_len = self.strategy_config.backward_window_length + self.strategy_config.forward_window_length

		for chart in input_chart_group.charts:
			data: pandas.DataFrame = chart.data
			data = data.pct_change()
			chart.data = data
			chart.refresh_indicators()

		dataframe = input_chart_group.dataframe
		dataframe = dataframe.fillna(0)

		dataframe = getattr(dataframe, truncate_from)(truncate_len)
		if len(dataframe) < self.strategy_config.backward_window_length:
			raise Exception('If this error ever raised then implement padding...')

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

	def from_model_output(self, outputs: numpy.ndarray) -> dict[Chart, dict[Literal['high', 'low'], float]]:
		return [
			(
				chart,
				{
					'high': output[0],
					'low': output[1]
				}
			)
			for chart, output in zip(self.strategy_config.output_chart_group.charts, outputs)
		]