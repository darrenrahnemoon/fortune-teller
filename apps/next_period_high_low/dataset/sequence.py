import functools
import pandas

from dataclasses import dataclass, field
from keras.utils.data_utils import Sequence

from core.repository import SimulationRepository
from core.utils.logging import Logger

from apps.next_period_high_low.preprocessor import NextPeriodHighLowPreprocessorService
from apps.next_period_high_low.config import NextPeriodHighLowStrategyConfig
from core.tensorflow.dataset.sequence import sequence_dataclass_kwargs

logger = Logger(__name__)

@dataclass(**sequence_dataclass_kwargs)
class NextPeriodHighLowSequence(Sequence):
	strategy_config: NextPeriodHighLowStrategyConfig = None
	preprocessor_service: NextPeriodHighLowPreprocessorService = None
	repository: SimulationRepository = field(default_factory = SimulationRepository)

	def __len__(self):
		return len(self.timestamps)

	def __getitem__(self, index):
		input_chart_group = self.strategy_config.observation.build_chart_group()
		output_chart_group = self.strategy_config.action.build_chart_group()
		timestamp = self.timestamps[index]

		input_chart_group.read(
			repository = self.repository,
			to_timestamp = timestamp, #inclusive
			count = self.strategy_config.observation.bars,
		)
		output_chart_group.read(
			repository = self.repository,
			from_timestamp = timestamp, # inclusive
			count = self.strategy_config.action.bars + 1,
		)
		output_chart_group.dataframe = output_chart_group.dataframe[1:] # remove the inclusive end to prevent hindsight

		x = self.preprocessor_service.to_model_input(input_chart_group)
		if type(x) == type(None):
			return

		y = self.preprocessor_service.to_model_output(output_chart_group)
		if type(y) == type(None):
			return

		return x, y

	@property
	@functools.cache
	def timestamps(self):
		timestamps = pandas.date_range(
			self.common_time_window.from_timestamp,
			self.common_time_window.to_timestamp - pandas.Timedelta(self.strategy_config.observation.bars + self.strategy_config.action.bars, 'minute'),
			freq='min'
		)
		timestamps = [
			timestamp
			for timestamp in timestamps
			if self.strategy_config.action.conditions.is_trading_hours(timestamp)
		]
		return timestamps

	@property
	@functools.cache
	def common_time_window(self):
		input_chart_group = self.strategy_config.observation.build_chart_group()
		return self.repository.get_common_time_window(input_chart_group)
