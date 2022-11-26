import pandas

from core.chart.chart import Chart

class ChartGroup:
	def __init__(
		self,
		charts: list[Chart] = None,
		**common_chart_params
	) -> None:
		self.dataframe: pandas.DataFrame = None
		self.charts: list[Chart] = []
		self.common_chart_params = common_chart_params

		for chart in charts:
			self.add_chart(chart)

	def add_chart(self, chart: Chart):
		for key, value in self.common_chart_params.items():
			setattr(chart, key, value)

		if type(self.dataframe) != pandas.DataFrame:
			self.dataframe = chart.dataframe
		else:
			self.dataframe = pandas.concat([ self.dataframe, chart.dataframe ], axis=1, copy=False)

		self.charts.append(chart)

	def read(self):
		for chart in self.charts:
			chart.read()