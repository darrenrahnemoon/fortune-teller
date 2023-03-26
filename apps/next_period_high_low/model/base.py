
import math
from dataclasses import dataclass

from keras import Model
from keras.layers import Input, Dense, Conv1D, Add, Dropout, Flatten, LSTM, Reshape
from keras.optimizers import Adam
from keras_tuner import HyperParameters

from apps.next_period_high_low.config import NextPeriodHighLowStrategyConfig
from core.tensorflow.tuner.hyperparameters import HyperParameterName
from core.tensorflow.model.service import ModelService

@dataclass
class NextPeriodHighLowModelService(ModelService):
	strategy_config: NextPeriodHighLowStrategyConfig = None

	def build(
		self,
		hyperparameters: HyperParameters = None
	):
		inputs = self.build_inputs()
		features_length = inputs.shape[-1]
		hyperparameter_name = HyperParameterName()

		def dropout_parameter(name: str):
			return hyperparameters.Float(
				name = name,
				min_value = 0.01,
				max_value = 0.99,
				step = 0.01
			)

		flows = []
		for parallel_flow_index in range(
			hyperparameters.Int(
				name = 'parallel_flows_count',
				min_value = 1,
				max_value = 5
			)
		):
			flow = inputs
			with hyperparameter_name.prefixed('flow', parallel_flow_index):
				for cnn_index in range(
					hyperparameters.Int(
						name = 'cnn_layers_count',
						min_value = 1,
						max_value = 4
					)
				):
					with hyperparameter_name.prefixed(f'cnn_{cnn_index}'):
						flow = Conv1D(
							name = hyperparameter_name.build('conv1d'),
							filters = hyperparameters.Int(
								name = hyperparameter_name.build('filters_count'),
								min_value = 1,
								max_value = features_length
							),
							kernel_size = hyperparameters.Int(
								name = hyperparameter_name.build('kernel_size'),
								min_value = 2,
								max_value = self.strategy_config.backward_window_bars
							),
							padding = 'same',
							activation = 'relu'
						)(flow)
						flow = Dropout(
							name = hyperparameter_name.build('dropout'),
							rate = dropout_parameter(hyperparameter_name.build('dropout'))
						)(flow)

				lstm_layers_count = hyperparameters.Int(
					name = 'lstm_layers_count',
					min_value = 1,
					max_value = 4
				)
				for lstm_index in range(lstm_layers_count):
					is_last_lstm = lstm_index == lstm_layers_count - 1

					with hyperparameter_name.prefixed(f'lstm_{lstm_index}'):
						flow = LSTM(
							name = hyperparameter_name.build('lstm'),
							units = hyperparameters.Int(
								name = 'last_lstm_units' if is_last_lstm else hyperparameter_name.build('units'),
								min_value = 1,
								max_value = features_length,
							),
							return_sequences = not is_last_lstm
						)(flow)
						flow = Dropout(
							name = hyperparameter_name.build('dropout'),
							rate = dropout_parameter(hyperparameter_name.build('dropout'))
						)(flow)

				flows.append(flow)
		y = Add()(flows)
		y = Flatten()(y)

		for index in range(
			hyperparameters.Int(
				name = 'dense_layers_count',
				min_value = 1,
				max_value = 4,
			)
		):
			with hyperparameter_name.prefixed(f'dense_{index}'):
				y = Dense(
					units = hyperparameters.Int(
						name = hyperparameter_name.build('units'),
						min_value = 64,
						max_value = 4096
					),
					activation = 'relu',
				)(y)
				y = Dropout(
					rate = dropout_parameter(hyperparameter_name.build('dropout'))
				)(y)

		outputs = self.build_outputs(y)

		model = Model(
			inputs = inputs,
			outputs = outputs
		)

		return model

	def build_inputs(self) -> Input:
		input_chart_group = self.strategy_config.input_chart_group
		features_length = 0
		for chart in input_chart_group.charts:
			features_length += len(chart.select)
			for indicator in chart.indicators.values():
				features_length += len(indicator.value_fields)
		return Input(
			batch_size = self.dataset_service.config.batch_size,
			shape = (self.strategy_config.backward_window_bars, features_length)
		)

	def build_outputs(self, x):
		output_chart_group = self.strategy_config.output_chart_group
		output_shape = (len(output_chart_group.charts), 2)
		x = Dense(math.prod(iter(output_shape)))(x)
		x = Reshape(output_shape)(x)
		return x
