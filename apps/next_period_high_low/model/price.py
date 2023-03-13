import math
from dataclasses import dataclass
from keras.layers import Dense, Reshape
from keras.optimizers import Adam
from keras_tuner import HyperParameters

from apps.next_period_high_low.model.base import NextPeriodHighLowModelService

@dataclass
class NextPeriodHighLowPriceModelService(NextPeriodHighLowModelService):
	def compile(self, parameters: HyperParameters):
		model = self.build(parameters)
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

	def build_outputs(self, x):
		output_chart_group = self.strategy_config.output_chart_group
		output_shape = (len(output_chart_group.charts), 2)
		x = Dense(math.prod(iter(output_shape)))(x)
		x = Reshape(output_shape)(x)
		return x
