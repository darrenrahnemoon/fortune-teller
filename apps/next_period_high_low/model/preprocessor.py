import pandas
from dataclasses import dataclass

from core.chart.group import ChartGroup

@dataclass
class NextPeriodHighLowPreprocessor:
	forward_window_length: int = None
	backward_window_length: int = None

	def process_input(
		self,
		input_chart_group: ChartGroup,
		is_training = False
	):
		for chart in input_chart_group.charts:
			data: pandas.DataFrame = chart.data
			data = data.pct_change()
			chart.data = data
			chart.refresh_indicators()

		dataframe = input_chart_group.dataframe
		dataframe = dataframe.fillna(0)

		if not is_training:
			dataframe = dataframe.tail(self.backward_window_length)
			if len(dataframe) < self.backward_window_length:
				pass # SHOULD DO: pad beginning of dataframe with zeros

		input_chart_group.dataframe = dataframe

	def to_model_input(self, input_chart_group: ChartGroup):
		return input_chart_group.dataframe.to_numpy()

	def to_model_output(self, output_chart_group: ChartGroup) -> dict:
		outputs = []
		for chart in output_chart_group.charts:
			outputs.append([
				chart.data['high'].max(),
				chart.data['low'].min()
			])
		return outputs