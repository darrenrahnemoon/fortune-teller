import functools
import pandas
import itertools

from dataclasses import dataclass, field
from keras.utils.data_utils import Sequence

from core.trading.repository import SimulationRepository
from core.utils.logging import Logger

from examples.ave_maria.tensorflow.preprocessor.service import AveMariaPreprocessorService
from examples.ave_maria.trading.config import AveMariaTradingConfig
from core.tensorflow.dataset.sequence import sequence_dataclass_kwargs

logger = Logger(__name__)

@dataclass(**sequence_dataclass_kwargs)
class AveMariaSequence(Sequence):
	trading_config: AveMariaTradingConfig = None
	preprocessor_service: AveMariaPreprocessorService = None
	repository: SimulationRepository = field(default_factory = SimulationRepository)

	def __len__(self):
		return len(self.timestamps)

	def __getitem__(self, index):
		input_chart_groups = self.trading_config.observation.build_chart_group()
		output_chart_group = self.trading_config.action.build_chart_group()
		timestamp = self.timestamps[index]

		for chart_group in input_chart_groups.values():
			chart_group.read(
				repository = self.repository,
				to_timestamp = timestamp, #inclusive
				count = self.trading_config.observation.bars + 1,
			)
			chart_group.dataframe = chart_group.dataframe[:-1] # remove the inclusive end to prevent hindsight

		output_chart_group.read(
			repository = self.repository,
			from_timestamp = timestamp, # inclusive
			count = self.trading_config.action.bars + 1,
		)
		output_chart_group.dataframe = output_chart_group.dataframe[1:] # remove the inclusive end to prevent hindsight

		x = self.preprocessor_service.to_model_input(input_chart_groups)
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
			self.common_time_window.to_timestamp,
			freq='min'
		)
		timestamps = [
			timestamp
			for timestamp in timestamps
			if self.trading_config.action.conditions.is_trading_hours(timestamp)
		]
		return timestamps

	@property
	@functools.cache
	def common_time_window(self):
		input_chart_groups = self.trading_config.observation.build_chart_group()
		charts = [ chart_group.charts for chart_group in input_chart_groups.values() ]
		return self.repository.get_common_time_window(
			list(itertools.chain(*charts))
		)