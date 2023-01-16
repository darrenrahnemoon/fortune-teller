import pandas
import inspect
from typing import TYPE_CHECKING, ClassVar
from dataclasses import dataclass, field

if TYPE_CHECKING:
	from core.indicator import Indicator
	from core.chart.group import ChartGroup
	from core.repository import Repository

from core.utils.shared_dataframe_container import SharedDataFrameContainer
from core.utils.time import TimeWindow, now
from core.utils.logging import logging

logger = logging.getLogger(__name__)

Symbol = str

@dataclass
class Chart(TimeWindow, SharedDataFrameContainer):
	symbol: Symbol = None
	repository: 'Repository' = None
	chart_group: 'ChartGroup' = None
	indicators: dict[str, 'Indicator'] = field(repr=False, default_factory=dict)
	count: int = None
	select: list[str] = None

	timestamp_field: ClassVar[str] = 'timestamp'
	query_fields: ClassVar[list[str]] = [ 'symbol' ]
	data_fields: ClassVar[list[str]] = []
	volume_fields: ClassVar[list[str]] = []

	@classmethod
	@property
	def value_fields(cls):
		return cls.data_fields + cls.volume_fields

	def __post_init__(self):
		super().__post_init__()
		self.dataframe = None
		self.select = self.select or self.value_fields
		for name, indicator in self.indicators.items():
			self.attach_indicator(indicator, name=name)

	def read(self, refresh_indicators = True, repository = None, **overrides):
		self.dataframe = (repository or self.repository).read_chart(self, **overrides)

		if refresh_indicators:
			self.refresh_indicators()
		return self

	@property
	def dataframe(self):
		"""
		Returns:
			pandas.DataFrame:
				The dataframe of the chart itself if it's been populated
				Otherwise, the dataframe of the chart group it belongs too
		"""
		dataframe = self._dataframe
		if type(dataframe) != pandas.DataFrame and self.chart_group:
			dataframe = self.chart_group.dataframe
		return dataframe

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
class ChartParams:
	chart: Chart = None
	overrides: dict = field(default_factory = dict)

	def __init__(
		self,
		chart: Chart or 'ChartParams',
		overrides: dict = {}
	) -> None:
		self.overrides = overrides
		if type(chart) == ChartParams:
			self.chart = chart.chart
			self.overrides.update(chart.overrides)
		else:
			self.chart = chart

	def __getitem__(self, name: str):
		# HACK: `type` is a special case as the class type is used during querying as well
		if name == 'type' or name == 'chart':
			if self.chart != None:
				return type(self.chart)
			else:
				return self.overrides.get('type', None)

		if name in self.overrides:
			return self.overrides[name]
		if hasattr(self.chart, name):
			return getattr(self.chart, name)
		return None

	def __setitem__(self, key, value):
		self.overrides[key] = value
