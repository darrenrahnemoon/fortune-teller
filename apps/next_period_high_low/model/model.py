
import math
from typing import Callable
from dataclasses import dataclass
from dataclasses import dataclass

from keras import Model
from keras.layers import Input, Dense, Conv1D, Add, Dropout, Flatten, LSTM, Reshape
from keras_tuner import HyperParameters

from core.chart import ChartGroup

@dataclass
class NextPeriodHighLowModel:
	build_input_chart_group: Callable[..., ChartGroup] = None
	build_output_chart_group: Callable[..., ChartGroup] = None

	forward_window_length: int = None
	backward_window_length: int = None

	batch_size: int = False

	def build(self, parameters: HyperParameters):
		inputs = self.build_inputs()

		dropout_rate = parameters.Float('dropout_rate', min_value = 0.2, max_value = 0.9, step = 0.05)
		parallel_flows_count = parameters.Int('parallel_flows_count', min_value = 2, max_value = 15)
		filters_count = parameters.Int('filters_count', min_value = 8, max_value = 1024)
		lstm_units = parameters.Int('lstm_units', min_value = 16, max_value = 1024)

		y = []
		for index in range(parallel_flows_count):
			_y = Conv1D(filters = filters_count, kernel_size = 2 ** (index + 4), padding = 'same')(inputs)
			_y = Dropout(dropout_rate)(_y)

			_y = Conv1D(filters = filters_count, kernel_size = 2 ** (index + 2), padding = 'same')(_y)
			_y = Dropout(dropout_rate)(_y)

			_y = LSTM(lstm_units)(_y)
			_y = Dropout(dropout_rate)(_y)

			y.append(_y)
		y = Add()(y)
		y = Flatten()(y)

		for index in range(parameters.Int('fully_connected_layer_count', min_value = 2, max_value = 5)):
			y = Dense(parameters.Int(f'fully_connected_layer_{index}_nodes', min_value = 2 ** 6, max_value = 2 ** 14))(y)
			y = Dropout(dropout_rate)(y)

		outputs = self.build_outputs(y)

		model = Model(
			inputs = inputs,
			outputs = outputs
		)
		model.compile(
			optimizer = parameters.Choice('optimizer', [ 'adam', 'sgd' ]),
			loss = 'mse',
			metrics = [ 'accuracy' ]
		)
		return model

	def build_inputs(self):
		input_chart_group = self.build_input_chart_group()
		features_length = 0
		for chart in input_chart_group.charts:
			features_length += len(chart.select)
			for indicator in chart.indicators.values():
				features_length += len(indicator.value_fields)
		return Input(
			batch_size = self.batch_size,
			shape = (self.backward_window_length, features_length)
		)

	def build_outputs(self, x):
		output_chart_group = self.build_output_chart_group()
		output_shape = (len(output_chart_group.charts), 2)
		x = Dense(math.prod(iter(output_shape)))(x)
		x = Reshape(output_shape)(x)
		return x
