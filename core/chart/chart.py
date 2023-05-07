import pandas
import inspect
from typing import TYPE_CHECKING, ClassVar
from dataclasses import dataclass, field

if TYPE_CHECKING:
	from core.indicator import Indicator
	from core.chart.group import ChartGroup
	from core.repository import Repository

from core.utils.dataframe_container import DataFrameContainer
from core.utils.time import TimeWindow, now
from core.utils.logging import Logger

logger = Logger(__name__)

Symbol = str

@dataclass
class Chart(TimeWindow, DataFrameContainer):
	symbol: Symbol = None
	repository: 'Repository' = None
	chart_group: 'ChartGroup' = None
	indicators: dict[str, 'Indicator'] = field(repr=False, default_factory=dict)
	count: int = None
	select: list[str] = field(default_factory = list)

	timestamp_field_name: ClassVar[str] = 'timestamp'
	query_field_names: ClassVar[list[str]] = DataFrameContainer.query_field_names + [ 'symbol' ]
	data_field_names: ClassVar[list[str]] = []
	volume_field_names: ClassVar[list[str]] = []
	spread_field_names: ClassVar[list[str]] = []

	@classmethod
	@property
	def value_field_names(cls):
		return DataFrameContainer.value_field_names + cls.data_field_names + cls.volume_field_names + cls.spread_field_names

	def __post_init__(self):
		super().__post_init__()
		self.dataframe = None
		if len(self.select) == 0:
			self.select = self.value_field_names

		for name, indicator in self.indicators.items():
			self.attach_indicator(indicator, name=name)

	def read(
		self,
		refresh_indicators = True,
		repository = None,
		**overrides
	):
		repository = repository or self.repository
		self.dataframe = repository.read_chart(self, **overrides)

		if refresh_indicators:
			self.refresh_indicators()
		return self

	@property
	def dataframe(self):
		"""
		Returns:
			pandas.DataFrame:
				The dataframe of the chart itself if it's been populated
				Otherwise, the dataframe of the chart group it belongs to
		"""
		if type(self._dataframe) == pandas.DataFrame:
			return self._dataframe
		if self.chart_group:
			return self.chart_group.dataframe
		return None

	@dataframe.setter
	def dataframe(self, dataframe: pandas.DataFrame):
		self._dataframe = dataframe

	def attach_indicator(self, indicator: 'Indicator' or type['Indicator'], name: str = None):
		if inspect.isclass(indicator):
			indicator = indicator()
		self.indicators[name or type(indicator)] = indicator
		indicator.attach(self)
		return indicator

	def detach_indicator(self, name: str):
		self.indicators[name].detach()
		del self.indicators[name]

	def refresh_indicators(self):
		for indicator in self.indicators.values():
			indicator.refresh()

@dataclass
class OverriddenChart:
	chart: Chart = None
	overrides: dict = field(default_factory = dict)

	def __init__(
		self,
		chart: Chart or 'OverriddenChart',
		overrides: dict = {}
	) -> None:
		self.overrides = overrides
		if type(chart) == OverriddenChart:
			self.chart = chart.chart
			self.overrides.update(chart.overrides)
		else:
			self.chart = chart

	def __getattr__(self, name: str):
		return self[name]

	def __getitem__(self, name: str):
		if name in self.overrides:
			return self.overrides[name]
		if hasattr(self.chart, name):
			return getattr(self.chart, name)
		return None

	def __setitem__(self, key, value):
		self.overrides[key] = value
