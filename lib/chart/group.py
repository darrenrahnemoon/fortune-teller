from numpy import e
import pandas

from lib.chart.chart import Chart

class ChartGroup:
	def __init__(
		self,
		charts: list[Chart] = None,
		from_timestamp = None,
		to_timestamp = None,
	) -> None:
		self.dataframe = None
		self.charts = []
		self.from_timestamp = from_timestamp
		self.to_timestamp = to_timestamp

		for chart in charts:
			self.add_chart(chart)

	def add_chart(self, chart: Chart): 
		if type(self.dataframe) != pandas.DataFrame:
			self.dataframe = chart.dataframe
		else:
			self.dataframe = pandas.concat([ self.dataframe, chart.dataframe ], axis=1, copy=False)
		self.charts.append(chart)
