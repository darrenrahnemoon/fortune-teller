import functools
import pandas
import inspect
import typing
import logging
from dataclasses import dataclass, field

if typing.TYPE_CHECKING:
	from core.indicator import Indicator
	from core.broker import Broker

from core.utils.time import TimeWindow

logger = logging.getLogger(__name__)

Symbol = str

@dataclass
class Chart(TimeWindow):
	query_fields: typing.ClassVar[list[str]] = [ 'symbol' ]
	value_fields: typing.ClassVar[list[str]] = []

	symbol: Symbol = None
	broker: 'Broker' = None
	indicators: dict[str, 'Indicator' or type['Indicator']] = field(repr=False, default_factory=dict)
	_dataframe: pandas.DataFrame = field(repr=False, init=False, default=None)

	def __post_init__(self):
		super().__post_init__()
		if len(self.indicators):
			indicators = self.indicators
			self.indicators = dict()
			for name, indicator in indicators.items():
				self.add_indicator(indicator, name=name)

	def __len__(self) -> int:
		return len(self.dataframe) if type(self.dataframe) == pandas.DataFrame else 0

	@functools.cached_property
	def name(self):
		return f"{type(self).__name__}.{'.'.join([ str(getattr(self, key)) for key in self.query_fields ])}"

	@property
	def data(self):
		if len(self.value_fields) == 1:
			return self.dataframe[self.symbol, self.name, self.value_fields[-1]]
		return self.dataframe[self.symbol, self.name]

	def read(self, broker: 'Broker' = None):
		self.broker = broker or self.broker
		self.broker.read_chart(self)
		return self

	def write(self, broker: 'Broker'):
		broker.write_chart(self)
		return self

	@property
	def dataframe(self):
		return self._dataframe

	@dataframe.setter
	def dataframe(self, dataframe: pandas.DataFrame):
		logger.debug(f'Setting dataframe for chart...\n{self}\n\n{dataframe}')
		if type(dataframe) != pandas.DataFrame:
			logger.error(f'Invalid dataframe was assigned to {self}: {dataframe}')
			return

		if len(dataframe) == 0:
			dataframe = pandas.DataFrame(columns=self.value_fields + [ 'timestamp' ])

		if dataframe.index.name != 'timestamp':
			dataframe['timestamp'] = pandas.to_datetime(dataframe['timestamp'])
			dataframe.set_index('timestamp', inplace=True, drop=True)
			dataframe.index.name = 'timestamp' # probably unnecessary someone check

		if type(dataframe.columns) != pandas.MultiIndex:
			dataframe = dataframe[[ key for key in self.value_fields ]]
			dataframe.columns = pandas.MultiIndex.from_tuples(
				[ (self.symbol, self.name, column) for column in dataframe.columns ],
				names=[ 'symbol', 'timeseries', 'feature' ]
			)

		if type(self._dataframe) != pandas.DataFrame:
			self._dataframe = dataframe
		else:
			self._dataframe = pandas.concat([ self._dataframe, dataframe ], axis=1, copy=False)

		self.refresh_indicators()

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