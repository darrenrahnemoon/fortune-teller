import pandas
import logging

from core.chart import Chart
from core.utils.cls import instance_to_repr

logger = logging.getLogger(__name__)

class Indicator:
	query_fields: list[str] = []
	value_fields: list[str] = []

	def __init__(self, **kwargs) -> None:
		self.chart: Chart = None
		self.name: str = None
		for key, value in kwargs.items():
			setattr(self, key, value)

	def __repr__(self) -> str:
		return instance_to_repr(self, self.query_fields)

	def __len__(self) -> int:
		data = self.data
		return len(data) if type(data) in [ pandas.DataFrame, pandas.Series ] else 0

	@property
	def data(self):
		if not self.chart:
			logger.error('Indicator is not attached to any chart but data was requested.')
			return
		if len(self.value_fields) == 1:
			return self.chart.dataframe[self.chart.symbol, self.name, self.value_fields[-1]]
		return self.chart.dataframe[self.chart.symbol, self.name]

	def apply(self, chart: Chart, force = False):
		self.chart = chart
		if type(chart.dataframe) != pandas.DataFrame:
			return

		if force\
			or self.name not in self.chart.dataframe.columns.get_level_values(1)\
			or self.chart.dataframe[self.chart.symbol, self.name].isna().values.any():
			value = self.run(self.chart.data)

			if (type(value) != dict):
				value = { self.value_fields[-1] : value }
			for key, value in value.items():
				self.chart.dataframe[self.chart.symbol, self.name, key] = value

	def run(self, dataframe: pandas.DataFrame) -> dict[str, pandas.Series] or pandas.Series:
		pass
