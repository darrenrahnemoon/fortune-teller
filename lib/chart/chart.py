import functools
import pathlib
import pandas
import inspect
import typing

if typing.TYPE_CHECKING:
	from lib.indicator import Indicator
	from lib.broker import Broker

from lib.utils.cls import ensureattr
from lib.utils.time import normalize_timestamp

class Chart:
	broker: 'Broker' # Globally set a default broker for a chart
	query_fields: list[str] = [ 'symbol' ]
	value_fields: list[str] = [ 'timestamp' ]

	def __init__(self,
		symbol: str = None,
		from_timestamp: pandas.Timestamp = None,
		to_timestamp: pandas.Timestamp = None,
		dataframe: pandas.DataFrame = None, 
		indicators: dict[str, 'Indicator' or type['Indicator']] = dict(),
		broker: 'Broker' = None,
		**kwargs
	):
		self.symbol = symbol
		self.from_timestamp = normalize_timestamp(from_timestamp)
		self.to_timestamp = normalize_timestamp(to_timestamp)

		if broker:
			self.broker = broker

		for key in self.query_fields:
			ensureattr(self, key, kwargs.get(key, None))

		self.dataframe: pandas.DataFrame = None
		if dataframe:
			self.load_dataframe(dataframe)

		self.indicators: dict[str, 'Indicator'] = dict()
		for name, indicator in indicators.items():
			self.add_indicator(indicator, name=name)

	def __repr__(self) -> str:
		return f"{type(self).__name__}({', '.join([ f'{key}={getattr(self, key)}' for key in self.query_fields ])})"

	def __len__(self) -> int:
		return len(self.dataframe) if type(self.dataframe) == pandas.DataFrame else 0

	@functools.cached_property
	def name(self):
		return f"{type(self).__name__}_{'_'.join([ str(getattr(self, key)) for key in self.query_fields ])}"

	@property
	def data(self):
		if len(self.value_fields) == 2: # first column is always timestamp
			return self.dataframe[self.symbol, self.name, self.value_fields[-1]]
		return self.dataframe[self.symbol, self.name]

	def read(self):
		self.broker.read(self)
		return self

	def load_dataframe(self, dataframe: pandas.DataFrame):
		if len(dataframe) == 0:
			dataframe = pandas.DataFrame(columns=self.value_fields)

		if dataframe.index.name != 'timestamp':
			timestamp_column = next(column for column in dataframe.columns if 'time' in column or 'date' in column)
			dataframe['timestamp'] = pandas.to_datetime(dataframe[timestamp_column])
			if timestamp_column != 'timestamp':
				dataframe.drop(columns=[timestamp_column], inplace=True)
			dataframe.set_index('timestamp', inplace=True, drop=True)
			dataframe.index.name = 'timestamp' # probably unnecessary someone check

		if type(dataframe.columns) != pandas.MultiIndex:
			dataframe = dataframe[[ key for key in self.value_fields if key != 'timestamp' ]]
			dataframe.columns = pandas.MultiIndex.from_tuples(
				[ (self.symbol, self.name, column) for column in dataframe.columns ],
				names=[ 'symbol', 'timeseries', 'feature' ]
			)

		if type(self.dataframe) == pandas.DataFrame:
			self.dataframe = pandas.concat([ dataframe, self.dataframe ], axis=1, copy=False)
		else:
			self.dataframe = dataframe
		self.refresh_indicators()

	def load_csv(self, path: pathlib.Path or str):
		path = str(path)
		dataframe = pandas.read_csv(path)
		dataframe.columns = [ column.lower() for column in dataframe.columns ]
		self.load_dataframe(dataframe)
		self.to_timestamp = dataframe.index[-1]
		self.from_timestamp = dataframe.index[0]

	def add_indicator(self, indicator: 'Indicator' or type['Indicator'], name: str = None):
		if inspect.isclass(indicator):
			indicator()
		indicator.name = name
		indicator.apply(self)
		self.indicators[indicator.name] = indicator
		return self

	def remove_indicator(self, name: str):
		del self.indicators[name]
		self.dataframe.drop((self.symbol, name), axis=1, inplace=True)

	def refresh_indicators(self, force: bool = False):
		for indicator in self.indicators.values():
			indicator.apply(self, force=force)