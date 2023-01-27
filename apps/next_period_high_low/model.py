
import math
from dataclasses import dataclass

from keras import Model
from keras.layers import Input, Dense, Conv1D, Add, Dropout, Flatten, LSTM, Reshape
from keras.optimizers import Adam
from keras_tuner import HyperParameters

from apps.next_period_high_low.config import NextPeriodHighLowStrategyConfig
from core.tensorflow.tuner.parameters import ParameterName
from core.tensorflow.model.service import ModelService

@dataclass
class NextPeriodHighLowModelService(ModelService):
	strategy_config: NextPeriodHighLowStrategyConfig = None

	def build(self, parameters: HyperParameters):
		inputs = self.build_inputs()
		features_length = inputs.shape[-1]
		parameter = ParameterName()
		def dropout_parameter(name: str):
			return parameters.Float(
				name = name,
				min_value = 0.01,
				max_value = 0.99,
				step = 0.01
			)

		flows = []
		for parallel_flow_index in range(
			parameters.Int(
				name = 'parallel_flows_count',
				min_value = 1,
				max_value = 5
			)
		):
			flow = inputs
			parameter.add_prefix('flow', parallel_flow_index)

			for cnn_index in range(
				parameters.Int(
					name = 'cnn_layers_count',
					min_value = 1,
					max_value = 4
				)
			):
				parameter.add_prefix(f'cnn_{cnn_index}')
				flow = Conv1D(
					name = parameter.name('conv1d'),
					filters = parameters.Int(
						name = parameter.name('filters_count'),
						min_value = 1,
						max_value = features_length
					),
					kernel_size = parameters.Int(
						name = parameter.name('kernel_size'),
						min_value = 2,
						max_value = self.strategy_config.backward_window_length
					),
					padding = 'same',
					activation = 'relu'
				)(flow)
				flow = Dropout(
					name = parameter.name('dropout'),
					rate = dropout_parameter(parameter.name('dropout'))
				)(flow)
				parameter.remove_prefix()

			lstm_layers_count = parameters.Int(
				name = 'lstm_layers_count',
				min_value = 1,
				max_value = 4
			)
			for lstm_index in range(lstm_layers_count):
				is_last_lstm = lstm_index == lstm_layers_count - 1

				parameter.add_prefix(f'lstm_{lstm_index}')
				flow = LSTM(
					name = parameter.name('lstm'),
					units = parameters.Int(
						name = 'last_lstm_units' if is_last_lstm else parameter.name('units'),
						min_value = 1,
						max_value = features_length,
					),
					return_sequences = not is_last_lstm
				)(flow)
				flow = Dropout(
					name = parameter.name('dropout'),
					rate = dropout_parameter(parameter.name('dropout'))
				)(flow)
				parameter.remove_prefix()

			flows.append(flow)
			parameter.remove_prefix()
		y = Add()(flows)
		y = Flatten()(y)

		for index in range(
			parameters.Int(
				name = 'dense_layers_count',
				min_value = 1,
				max_value = 4,
			)
		):
			parameter.add_prefix(f'dense_{index}')
			y = Dense(
				units = parameters.Int(
					name = parameter.name('units'),
					min_value = 64,
					max_value = 4096
				),
				activation = 'relu',
			)(y)
			y = Dropout(
				rate = dropout_parameter(parameter.name('dropout'))
			)(y)
			parameter.remove_prefix()

		outputs = self.build_outputs(y)

		model = Model(
			inputs = inputs,
			outputs = outputs
		)
		model.compile(
			optimizer = Adam(
				learning_rate = parameters.Float(
					name = 'adam_optimizer_learning_rate',
					min_value = 10 ** -4,
					max_value = 10 ** -3,
					step = 10 ** -4
				)
			),
			loss = 'mae',
			metrics = [ 'mae' ]
		)
		return model

	def build_inputs(self):
		input_chart_group = self.strategy_config.build_input_chart_group()
		features_length = 0
		for chart in input_chart_group.charts:
			features_length += len(chart.select)
			for indicator in chart.indicators.values():
				features_length += len(indicator.value_fields)
		return Input(
			batch_size = self.dataset.config.batch_size,
			shape = (self.strategy_config.backward_window_length, features_length)
		)

	def build_outputs(self, x):
		output_chart_group = self.strategy_config.build_output_chart_group()
		output_shape = (len(output_chart_group.charts), 2)
		x = Dense(math.prod(iter(output_shape)))(x)
		x = Reshape(output_shape)(x)
		return x
