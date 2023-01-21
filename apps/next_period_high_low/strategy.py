from dataclasses import dataclass
from typing import Callable

from core.repository import Repository
from core.chart import ChartGroup
from core.strategy import Strategy
from core.interval import Interval

from .model.service import NextPeriodHighLowService

@dataclass
class NextPeriodHighLowStrategy(Strategy):
	metatrader_repository: Repository = None 
	alphavantage_repository: Repository = None
	build_input_chart_group: Callable[..., ChartGroup] = None
	build_output_chart_group: Callable[..., ChartGroup] = None
	interval: Interval = None
	forward_window_length: int = None
	backward_window_length: int = None

	service: NextPeriodHighLowService = None
