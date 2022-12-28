import functools
import pandas
from typing import Callable
from dataclasses import dataclass
from keras.utils.data_utils import Sequence

from core.chart import ChartGroup
from core.broker.simulation import SimulationBroker
from .preprocessor import NextPeriodHighLowPreprocessor
from .repository import NextPeriodHighLowRepository
from core.utils.tensorflow.sequence import sequence_dataclass_kwargs

@dataclass(**sequence_dataclass_kwargs)
class NextPeriodHighLowSequence(Sequence):
	build_input_chart_group: Callable[..., ChartGroup] = None
	build_output_chart_group: Callable[..., ChartGroup] = None
	backward_window_length: int = None
	forward_window_length: int = None
	repository: NextPeriodHighLowRepository = None
	preprocessor: NextPeriodHighLowPreprocessor = None

	def __len__(self):
		return len(self.timestamps)

	def __getitem__(self, index):
		input_chart_group = self.build_input_chart_group()
		output_chart_group = self.build_output_chart_group()
		timestamp = self.timestamps[index]

		input_chart_group.set_fields({
			'from_timestamp': timestamp,
			'count': self.backward_window_length + self.forward_window_length
		})

		dataframe = self.repository.read_chart_group(input_chart_group)
		input_chart_group.dataframe = dataframe[:self.backward_window_length]
		output_chart_group.dataframe = dataframe[self.backward_window_length:]

		x = self.preprocessor.to_model_input(input_chart_group)
		y = self.preprocessor.to_model_output(output_chart_group)
		return x, y

	@property
	@functools.cache
	def timestamps(self):
		return pandas.date_range(
			self.common_time_window.from_timestamp,
			self.common_time_window.to_timestamp - pandas.Timedelta(self.backward_window_length + self.forward_window_length, 'minute'),
			freq='min'
		)

	@property
	@functools.cache
	def common_time_window(self):
		return SimulationBroker.get_common_time_window(self.build_input_chart_group())

	def cache(self, from_timestamp = None, to_timestamp = None):
		chart_group = self.build_input_chart_group()

		increments = list(pandas.date_range(
			start = from_timestamp or self.common_time_window.from_timestamp,
			end = to_timestamp or self.common_time_window.to_timestamp,
			freq = 'MS' # "Month Start"
		))
		increments.append(self.common_time_window.to_timestamp)

		chart_group.set_field('count', None)
		for index in range(1, len(increments)):
			chart_group.set_fields({
				'from_timestamp': increments[index - 1],
				'to_timestamp': increments[index],
			})
			chart_group.read()
			self.preprocessor.process_input(chart_group, is_training = True)
			self.repository.write_chart_group(chart_group)
