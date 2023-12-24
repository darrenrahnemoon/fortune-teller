
import math
from dataclasses import dataclass, fields

from keras import Model
from keras.layers import Input, Dense, Add, Conv1D, Flatten, LSTM, Reshape, Concatenate, MultiHeadAttention
from keras_tuner import HyperParameters

from apps.ave_maria.trading.config import AveMariaTradingConfig
from core.tensorflow.model.service import ModelService

@dataclass
class AveMariaModelService(ModelService):
	trading_config: AveMariaTradingConfig = None

	def build(
		self,
		hyperparameters: HyperParameters = None
	):
		# hyperparameter_name = HyperParameterName()
		inputs = self.build_inputs()
		y = []
		for chart in inputs:
			# MHA
			x = MultiHeadAttention(
				num_heads = 4,
				key_dim = chart.shape[-1],
				dropout = 0.6,
			)(chart, chart, chart)

			# LSTM
			x = LSTM(
				units = chart.shape[-1],
				return_sequences = True,
			)(x)
			y.append(x)

		y = Add()(y)
		y = Conv1D(
			kernel_size = 20,
			filters = 10,
		)(y)
		y = Flatten()(y)

		for _ in range(2):
			y = Dense(
				units = 512,
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
		input_chart_groups = self.trading_config.observation.build_chart_group()
		for interval, chart_group in input_chart_groups.items():
			features_length = 0
			for chart in chart_group.charts:
				features_length += len(chart.select)
				for indicator in chart.indicators.values():
					features_length += len(fields(indicator.Record))
			inputs.append(
				Input(
					shape = (self.trading_config.observation.bars, features_length),
					batch_size = self.dataset_service.config.batch_size,
					name = str(interval),
				)
			)
		return inputs

	def build_outputs(self, x):
		output_chart_group = self.trading_config.action.build_chart_group()

		high_low_shape = (len(output_chart_group.charts), 2)
		high_low = Dense(math.prod(iter(high_low_shape)))(x)
		high_low = Reshape(high_low_shape, name = 'high_low')(high_low)

		direction = [
			Reshape((1, 2))(
				Dense(2, activation = 'softmax', name = f'{chart.symbol}_direction')(x)
			)
			for chart in output_chart_group.charts
		]

		direction = Concatenate(axis = 1, name = 'direction')(direction)

		return {
			'direction' : direction,
			'high_low' : high_low,
		}
