import abc
import pandas

from typing import ClassVar
from dataclasses import dataclass

from core.utils.shared_dataframe_container import SharedDataFrameContainer
from core.chart import Chart
from core.utils.logging import Logger

logger = Logger(__name__)

@dataclass
class Indicator(SharedDataFrameContainer):
	value_fields: ClassVar[list[str]] = []

	def __post_init__(self) -> None:
		self.chart: Chart = None

	@property
	def name(self):
		return f'{super().name}({self.chart.name})'

	@property
	def dataframe(self):
		if self.chart:
			return self.chart.dataframe
		return None

	def attach(self, chart: Chart):
		self.chart = chart
		if len(chart) == 0:
			return
		self.refresh()

	def detach(self):
		self.chart.dataframe.drop(self.name, axis=1, inplace=True)
		self.chart = None

	def refresh(self):
		self.data = self.run(self.chart.data)

	@abc.abstractmethod
	def run(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
		pass
