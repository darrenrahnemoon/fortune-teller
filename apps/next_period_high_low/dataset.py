import functools
import pandas

from dataclasses import dataclass, field
from keras.utils.data_utils import Sequence

from core.repository import SimulationRepository
from core.utils.logging import Logger

from apps.next_period_high_low.preprocessor.base import NextPeriodHighLowPreprocessorService
from apps.next_period_high_low.config import NextPeriodHighLowStrategyConfig
from core.tensorflow.dataset.sequence import SkipItemException, sequence_dataclass_kwargs

logger = Logger(__name__)

@dataclass(**sequence_dataclass_kwargs)
class NextPeriodHighLowSequence(Sequence):
	strategy_config: NextPeriodHighLowStrategyConfig = None
	preprocessor_service: NextPeriodHighLowPreprocessorService = None
	repository: SimulationRepository = field(default_factory = SimulationRepository)

	def __len__(self):
		return len(self.timestamps)

	def __getitem__(self, index):
		input_chart_group = self.strategy_config.input_chart_group
		output_chart_group = self.strategy_config.output_chart_group
		timestamp = self.timestamps[index]

		input_chart_group.read(
			repository = self.repository,
			from_timestamp = timestamp,
			to_timestamp = None,
			count = self.strategy_config.backward_window_length + self.strategy_config.forward_window_length
		)
		dataframe = input_chart_group.dataframe.head(self.strategy_config.backward_window_length + self.strategy_config.forward_window_length)
		input_chart_group.dataframe = dataframe[:self.strategy_config.backward_window_length]
		output_chart_group.dataframe = dataframe[self.strategy_config.backward_window_length:]
		try:
			x = self.preprocessor_service.to_model_input(input_chart_group)
			y = self.preprocessor_service.to_model_output(output_chart_group)
			logger.debug(f'NextPeriodHighLowSequence[{index}] | {timestamp} -> x:{x.shape}, y:{y.shape}')
			return x, y
		except Exception:
			raise SkipItemException()

	@property
	@functools.cache
	def timestamps(self):
		timestamps = pandas.date_range(
			self.common_time_window.from_timestamp,
			self.common_time_window.to_timestamp - pandas.Timedelta(self.strategy_config.backward_window_length + self.strategy_config.forward_window_length, 'minute'),
			freq='min'
		)
		return [ timestamp for timestamp in timestamps if self.strategy_config.is_trading_hours(timestamp) ]

	@property
	@functools.cache
	def common_time_window(self):
		return self.repository.get_common_time_window(self.strategy_config.input_chart_group)
