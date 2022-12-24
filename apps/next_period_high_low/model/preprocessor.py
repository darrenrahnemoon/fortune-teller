from core.chart.serializers import MULTI_INDEX_COLUMN_SEPARATOR
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
		inputs = {}
		for column in input_chart_group.dataframe:
			series = input_chart_group.dataframe[column]
			inputs[MULTI_INDEX_COLUMN_SEPARATOR.join(column)] = series.to_numpy()

		return inputs

	def to_model_output(self, output_chart_group: ChartGroup) -> dict:
		outputs = {}
		for column in output_chart_group.dataframe.columns:
			if column[-1] == 'high':
				outputs[column] = output_chart_group.dataframe[column].max()
			if column[-1] == 'low':
				outputs[column] = output_chart_group.dataframe[column].min()
		return outputs