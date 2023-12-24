import functools
import pandas
import itertools

from dataclasses import dataclass, field
from keras.utils.data_utils import Sequence

from core.chart import CandleStickChart
from core.repository import SimulationRepository
from core.utils.logging import Logger
from core.interval import Interval

from apps.pelosi_predictor.preprocessor import PelosiPredictorPreprocessorService
from apps.pelosi_predictor.config import PelosiPredictorStrategyConfig
from core.tensorflow.dataset.sequence import sequence_dataclass_kwargs

logger = Logger(__name__)

@dataclass(**sequence_dataclass_kwargs)
class PelosiPredictorSequence(Sequence):
	strategy_config: PelosiPredictorStrategyConfig = None
	repository_lag = pandas.Timedelta(1, 'day')
	preprocessor_service: PelosiPredictorPreprocessorService = None
	repository: SimulationRepository = field(default_factory = SimulationRepository)

	def __len__(self):
		return len(self.timestamps)

	def __getitem__(self, index):
		input_chart_groups = self.strategy_config.observation.build_chart_group()
		output_chart_group = self.strategy_config.action.build_chart_group()
		timestamp = self.timestamps[index]

		for chart_class, chart_group in input_chart_groups.items():
			to_timestamp = timestamp
			if chart_class != CandleStickChart:
				to_timestamp -= self.repository_lag

			chart_group.read(
				repository = self.repository,
				to_timestamp = to_timestamp,
			)

		output_chart_group.read(
			repository = self.repository,
			from_timestamp = timestamp,
		)

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
			if self.strategy_config.action.conditions.is_trading_hours(timestamp)
		]
		return timestamps

	@property
	@functools.cache
	def common_time_window(self):
		input_chart_groups = self.strategy_config.observation.build_chart_group()
		charts = [ chart_group.charts for chart_group in input_chart_groups.values() ]
		return self.repository.get_common_time_window(
			list(itertools.chain(*charts))
		)
