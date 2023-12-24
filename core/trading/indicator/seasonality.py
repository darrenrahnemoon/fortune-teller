import pandas
import numpy
from dataclasses import dataclass, make_dataclass, field

from core.trading.indicator import Indicator

@dataclass
class SeasonalityIndicator(Indicator):
	seasonality_metrics = {
		'year_of_century': lambda timestamp: timestamp.year % 100 / 100, 
		'quarter_of_year': lambda timestamp: (timestamp.quarter + 1) / 4,
		'month_of_year': lambda timestamp: timestamp.month / 12,
		'day_of_month': lambda timestamp: timestamp.day / 30.437,
		'day_of_week': lambda timestamp: (timestamp.dayofweek + 1) / 7,
		'day_of_year': lambda timestamp: timestamp.dayofyear / 365,
		'hour_of_day': lambda timestamp: timestamp.hour / 24,
		'minute_of_hour': lambda timestamp: timestamp.minute / 60,
	}

	Record = make_dataclass(
		'Record',
		[
			(f'{operation}_{key}', float, field(default = None))
			for key in seasonality_metrics.keys() 
			for operation in [ 'sin', 'cos' ]
		],
		bases = (Indicator.Record, )
	)

	def run(self, dataframe: pandas.DataFrame):
		result = pandas.DataFrame(index=dataframe.index)
		for seasonality, frequency in self.seasonality_metrics.items():
			result[f'sin_{seasonality}'] = numpy.sin(2 * numpy.pi * frequency(dataframe.index))
			result[f'cos_{seasonality}'] = numpy.cos(2 * numpy.pi * frequency(dataframe.index))
		return result