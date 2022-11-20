import pandas
import logging

from lib.chart import Chart

logger = logging.getLogger(__file__)

class Indicator:
	def __init__(self, name: str = None, **kwargs) -> None:
		self.name = name
		self.chart: Chart = None
		for key, value in kwargs.items():
			setattr(self, key, value)

	@property
	def name(self):
		return self._name or type(self).__name__

	@name.setter
	def name(self, value: str):
		self._name = value

	@property
	def data(self):
		if not self.chart:
			logger.error('Indicator is not attached to any chart but data was requested.')
			return
		data = self.chart.dataframe[self.chart.symbol, self.name]
		if len(data.columns) == 1:
			default_column = data.columns[0]
			series = data[default_column]
			series.name = default_column
			return series
		return 

	def apply(self, chart: Chart, force = False):
		self.chart = chart
		if type(chart.dataframe) != pandas.DataFrame:
			return

		if force\
			or self.name not in self.chart.dataframe.columns.get_level_values(1)\
			or self.chart.dataframe[self.chart.symbol, self.name].isna().values.any():
			value = self.run(self.chart.data)

			if (type(value) != dict):
				value = { 'value' : value }
			for key, value in value.items():
				self.chart.dataframe[self.chart.symbol, self.name, key] = value

	def run(self, dataframe: pandas.DataFrame) -> dict[str, pandas.Series] or pandas.Series:
		pass
