import pandas
import inspect
import logging
from typing import TYPE_CHECKING, ClassVar
from dataclasses import dataclass, field

if TYPE_CHECKING:
	from core.indicator import Indicator
	from core.chart.group import ChartGroup
	from core.broker import Broker

from core.utils.shared_dataframe_container import SharedDataFrameContainer
from core.utils.time import TimeWindow

logger = logging.getLogger(__name__)

Symbol = str

@dataclass
class Chart(TimeWindow, SharedDataFrameContainer):
	symbol: Symbol = None
	broker: 'Broker' = None
	chart_group: 'ChartGroup' = None
	indicators: dict[str, type['Indicator']] = field(repr=False, default_factory=dict)
	count: int = None
	select: list[str] = None

	query_fields: ClassVar[list[str]] = [ 'symbol' ]
	timestamp_field: ClassVar[str] = Chart.timestamp_field
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

	def read(self, refresh_indicators = True):
		self.broker.read_chart(self)
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
		if type(dataframe) != pandas.DataFrame:
			self._dataframe = dataframe
			return

		if len(dataframe) == 0:
			dataframe = pandas.DataFrame(columns = [ Chart.timestamp_field ] + self.value_fields)

		if type(dataframe.index) != pandas.DatetimeIndex:
			dataframe.index = pandas.DatetimeIndex(dataframe[Chart.timestamp_field], name=Chart.timestamp_field)
			if not dataframe.index.tz:
				dataframe.index = dataframe.index.tz_localize(tz='UTC')
			dataframe = dataframe.drop([ Chart.timestamp_field ], axis=1)

		if type(dataframe.columns) != pandas.MultiIndex:
			dataframe = dataframe[[ key for key in dataframe.columns if key in self.value_fields ]]
			dataframe.columns = pandas.MultiIndex.from_tuples(
				[ (self.name, column) for column in dataframe.columns ],
				names=[ 'timeseries', 'field' ]
			)
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