import typing
import pandas
from dataclasses import dataclass, field

if typing.TYPE_CHECKING:
	from core.broker.broker import Broker
from core.chart.chart import Chart

@dataclass
class ChartGroup:
	charts: list[Chart] = field(default_factory=list)
	dataframe: pandas.DataFrame = field(repr=False, init=False, default_factory=lambda: pandas.DataFrame(columns=pandas.MultiIndex(levels=[[], []], codes=[[], []])))
	common_params: dict[str] = field(default_factory=dict)

	def __post_init__(self):
		self.common_params['chart_group'] = self
		self.set_fields(self.common_params)

	def add_chart(self, chart: Chart):
		for key, value in self.common_params.items():
			setattr(chart, key, value)
		self.charts.append(chart)

	def set_fields(self, values: dict[str]):
		for chart in self.charts:
			for key, value in values.items():
				setattr(chart, key, value)

	def set_field(self, key: str, value):
		for chart in self.charts:
			setattr(chart, key, value)
		self.common_params[key] = value

	def read(self, refresh_indicators = True):
		for chart in self.charts:
			chart.read(refresh_indicators = refresh_indicators)

		dataframes = []
		for chart in self.charts:
			dataframes.append(chart.dataframe)
			chart.dataframe = None
		dataframe = pandas.concat(dataframes, axis=1)
		# dataframe = dataframe.reindex(dataframe.columns.sort_values(), axis=1)
		self.dataframe = dataframe