from core.repository.simulation import SimulationRepository
import functools
import pandas

from typing import Callable
from dataclasses import dataclass
from keras.utils.data_utils import Sequence

from core.chart import ChartGroup
from core.repository.simulation import SimulationRepository
from core.utils.logging import logging
from .preprocessor import NextPeriodHighLowPreprocessor
from core.utils.tensorflow.sequence import sequence_dataclass_kwargs

logger = logging.getLogger(__name__)

@dataclass(**sequence_dataclass_kwargs)
class NextPeriodHighLowSequence(Sequence):
	build_input_chart_group: Callable[..., ChartGroup] = None
	build_output_chart_group: Callable[..., ChartGroup] = None
	backward_window_length: int = None
	forward_window_length: int = None
	repository: SimulationRepository = None
	preprocessor: NextPeriodHighLowPreprocessor = None

	def __len__(self):
		return len(self.timestamps)

	def __getitem__(self, index):
		input_chart_group = self.build_input_chart_group()
		output_chart_group = self.build_output_chart_group()
		timestamp = self.timestamps[index]

		input_chart_group.read(
			repository = self.repository,
			from_timestamp = timestamp,
			to_timestamp = None,
			count = self.backward_window_length + self.forward_window_length
		)
		self.preprocessor.process_input(input_chart_group)

		output_chart_group.dataframe = input_chart_group.dataframe[self.backward_window_length:]
		input_chart_group.dataframe = input_chart_group.dataframe[:self.backward_window_length]
		x = self.preprocessor.to_model_input(input_chart_group)
		y = self.preprocessor.to_model_output(output_chart_group)
		logger.debug(f'NextPeriodHighLowSequence[{index}] | {timestamp} -> x:{x.shape}, y:{y.shape}')
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
		return self.repository.get_common_time_window(self.build_input_chart_group())
