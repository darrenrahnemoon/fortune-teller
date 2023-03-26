from dataclasses import dataclass
from core.chart import ChartGroup
from core.utils.logging import Logger

from apps.next_period_high_low.config import NextPeriodHighLowStrategyConfig
from core.tensorflow.preprocessor.service import PreprocessorService

logger = Logger(__name__)

@dataclass
class NextPeriodHighLowPreprocessorService(PreprocessorService):
	strategy_config: NextPeriodHighLowStrategyConfig = None

	def to_model_input(self, input_chart_group: ChartGroup):
		input_chart_group.dataframe = input_chart_group.dataframe.tail(self.strategy_config.backward_window_bars)
		for chart in input_chart_group.charts:
			chart.data = chart.data.pct_change()
		input_chart_group.dataframe = input_chart_group.dataframe.fillna(0)
		return input_chart_group.dataframe.to_numpy()
