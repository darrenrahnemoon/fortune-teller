import math
from dataclasses import dataclass
from keras.layers import Dense, Reshape

from apps.next_period_high_low.model.base import NextPeriodHighLowModelService

@dataclass
class NextPeriodHighLowPriceModelService(NextPeriodHighLowModelService):
	def build_outputs(self, x):
		output_chart_group = self.strategy_config.output_chart_group
		output_shape = (len(output_chart_group.charts), 4)
		x = Dense(math.prod(iter(output_shape)))(x)
		x = Reshape(output_shape)(x)
		return x
