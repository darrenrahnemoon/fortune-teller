
import math
from dataclasses import dataclass

from keras import Model
from keras.layers import Input, Dense, Conv1D, Add, Dropout, Flatten, LSTM, Reshape, Concatenate, MultiHeadAttention, LayerNormalization
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
		hyperparameter_name = HyperParameterName()
		inputs = self.build_inputs()
		y = []
		for chart in inputs:
			x = MultiHeadAttention(
				num_heads = 4,
				key_dim = chart.shape[-1],
				dropout = 0.7,
			)(chart, chart, chart)
			x = x + chart
			x = LayerNormalization()(x)
			y.append(x)

		y = Add()(y)
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

		outputs = self.build_outputs(y)

		model = Model(
			inputs = inputs,
			outputs = outputs
		)

		return model

	def build_inputs(self) -> Input:
		inputs = []
		input_chart_groups = self.strategy_config.observation.build_chart_group()
		for interval, chart_group in input_chart_groups.items():
			features_length = 0
			for chart in chart_group.charts:
				features_length += len(chart.select)
				for indicator in chart.indicators.values():
					features_length += len(indicator.value_field_names)

			inputs.append(
				Input(
					shape = (self.strategy_config.observation.bars, features_length),
					batch_size = self.dataset_service.config.batch_size,
					name = str(interval),
				)
			)
		return inputs

	def build_outputs(self, x):
		output_chart_group = self.strategy_config.action.build_chart_group()
		numerical_output_shape = (len(output_chart_group.charts), 2)
		numerical_output = Dense(math.prod(iter(numerical_output_shape)))(x)
		numerical_output = Reshape(numerical_output_shape)(numerical_output)

		direction_output_shape = (len(output_chart_group.charts), 1)
		direction_output = Dense(math.prod(iter(direction_output_shape)), activation = 'sigmoid')(x)
		direction_output = Reshape(direction_output_shape)(direction_output)

		y = Concatenate(axis = -1)([ numerical_output, direction_output ])
		return y
