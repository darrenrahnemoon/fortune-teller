import functools
import pathlib
import pandas
import inspect
import typing
import logging

if typing.TYPE_CHECKING:
	from lib.indicator import Indicator
	from lib.broker import Broker

from lib.utils.cls import ensureattr
from lib.utils.time import normalize_timestamp

logger = logging.getLogger(__name__)

class Chart:
	query_fields: list[str] = [ 'symbol' ]
	value_fields: list[str] = []

	def __init__(self,
		symbol: str = None,
		from_timestamp: pandas.Timestamp = None,
		to_timestamp: pandas.Timestamp = None,
		dataframe: pandas.DataFrame = None, 
		indicators: dict[str, 'Indicator' or type['Indicator']] = dict(),
		**kwargs
	):
		self.symbol = symbol
		self.from_timestamp = normalize_timestamp(from_timestamp)
		self.to_timestamp = normalize_timestamp(to_timestamp)

		for key in self.query_fields:
			ensureattr(self, key, kwargs.get(key, None))

		self.dataframe: pandas.DataFrame = None
		if dataframe:
			self.load_dataframe(dataframe)

		self.indicators: dict[str, 'Indicator'] = dict()
		for name, indicator in indicators.items():
			self.add_indicator(indicator, name=name)

	def __repr__(self) -> str:
		return f"{type(self).__name__}({', '.join([ f'{key}={getattr(self, key)}' for key in self.query_fields + [ 'from_timestamp', 'to_timestamp' ] if getattr(self, key) != None ])})"

	def __len__(self) -> int:
		return len(self.dataframe) if type(self.dataframe) == pandas.DataFrame else 0

	@functools.cached_property
	def _name(self):
		return f"{type(self).__name__}.{'.'.join([ str(getattr(self, key)) for key in self.query_fields ])}"

	@property
	def data(self):
		if len(self.value_fields) == 1:
			return self.dataframe[self.symbol, self._name, self.value_fields[-1]]
		return self.dataframe[self.symbol, self._name]

	def read(self, broker: 'Broker'):
		broker.read(self)
		return self

	def write(self, broker: 'Broker'):
		broker.write(self)
		return self

	def load_dataframe(self, dataframe: pandas.DataFrame):
		if type(dataframe) != pandas.DataFrame:
			logger.error(f'Invalid parameter was passed to `load_dataframe`: {dataframe}')
			return

		if len(dataframe) == 0:
			dataframe = pandas.DataFrame(columns=self.value_fields)

		if dataframe.index.name != 'timestamp':
			dataframe['timestamp'] = pandas.to_datetime(dataframe['timestamp'])
			dataframe.set_index('timestamp', inplace=True, drop=True)
			dataframe.index.name = 'timestamp' # probably unnecessary someone check

		if type(dataframe.columns) != pandas.MultiIndex:
			dataframe = dataframe[[ key for key in self.value_fields ]]
			dataframe.columns = pandas.MultiIndex.from_tuples(
				[ (self.symbol, self._name, column) for column in dataframe.columns ],
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
			indicator = indicator()

		indicator.name = name or repr(indicator)
		self.indicators[name or type(indicator)] = indicator

		indicator.apply(self)
		return indicator

	def remove_indicator(self, name: str):
		indicator = self.indicators[name]
		indicator.chart = None
		self.dataframe.drop((self.symbol, indicator.name), axis=1, inplace=True)
		del self.indicators[name]

	def refresh_indicators(self, force: bool = False):
		for indicator in self.indicators.values():
			indicator.apply(self, force=force)