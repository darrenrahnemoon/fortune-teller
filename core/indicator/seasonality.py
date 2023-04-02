import pandas
import numpy
from dataclasses import dataclass

from core.indicator import Indicator

@dataclass
class SeasonalityIndicator(Indicator):
	seasonality_metrics = {
		'year-century': lambda index: index.year % 100 / 100, 
		'quarter-year': lambda index: (index.quarter + 1) / 4,
		'month-year': lambda index: index.month / 12,
		'day-month': lambda index: index.day / 30.437,
		'day-week': lambda index: (index.dayofweek + 1) / 7,
		'day-year': lambda index: index.dayofyear / 365,
		'hour-day': lambda index: index.hour / 24,
		'minute-hour': lambda index: index.minute / 60,
	}
	value_field_names = Indicator.value_field_names + [
		f'{operation}({key})'
		for key in seasonality_metrics.keys() 
		for operation in [ 'sin', 'cos' ]
	]

	def run(self, dataframe: pandas.DataFrame):
		result = pandas.DataFrame(index=dataframe.index)
		for seasonality, frequency in self.seasonality_metrics.items():
			result[f'sin({seasonality})'] = numpy.sin(2 * numpy.pi * frequency(dataframe.index))
			result[f'cos({seasonality})'] = numpy.cos(2 * numpy.pi * frequency(dataframe.index))
		return result