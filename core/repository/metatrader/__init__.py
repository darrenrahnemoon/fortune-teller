import core.repository.metatrader.resolve

import numpy
import pandas
import MetaTrader5
from typing import TYPE_CHECKING
from dataclasses import dataclass

from .serializers import MetaTraderSerializers
from core.repository.repository import Repository
from core.utils.time import TimestampLike, normalize_timestamp
from core.chart import CandleStickChart, TickChart, Chart, OverriddenChart, Symbol

if TYPE_CHECKING:
	from core.order import OrderType
from core.utils.logging import Logger

logger = Logger(__name__)

@dataclass
class MetaTraderRepository(Repository):
	timezone = 'UTC'
	serializers = MetaTraderSerializers()

	def __post_init__(self):
		self._now = None
		if not MetaTrader5.initialize():
			raise MetaTrader5.last_error()

	@property
	def now(self) -> pandas.Timestamp:
		return self._now or super().now

	@now.setter
	def now(self, value: TimestampLike):
		self._now = normalize_timestamp(value)

	def get_available_symbols(self):
		return [
			symbol.name
			for symbol in MetaTrader5.symbols_get()
		]

	def get_all_available_charts(self, **kwargs):
		symbols = self.get_available_symbols()
		for symbol in symbols:
			for interval in self.serializers.interval.mapping.keys():
				yield CandleStickChart(
					symbol = symbol,
					interval = interval,
				)
			yield TickChart(symbol = symbol)

	def read_chart(
		self,
		chart: Chart or OverriddenChart = None,
		**overrides
	) -> pandas.DataFrame:
		chart = OverriddenChart(chart, overrides)
		dataframe = None
		if chart.type == CandleStickChart:
			dataframe = self.read_raw_candlestick_chart(chart)
			dataframe = self.ensure_interval_integrity(
				dataframe = dataframe,
				chart = chart
			)
		elif chart.type == TickChart:
			dataframe = self.read_raw_tick_chart(chart)

		return dataframe

	def read_raw_tick_chart(self, chart: TickChart):
		if chart.count:
			records = MetaTrader5.copy_ticks_from(
				chart.symbol,
				chart.to_timestamp.to_pydatetime(),
				chart.count,
				MetaTrader5.COPY_TICKS_ALL,
			)
		else:
			records = MetaTrader5.copy_ticks_range(
				chart.symbol,
				chart.from_timestamp.to_pydatetime(),
				chart.to_timestamp.to_pydatetime(),
				MetaTrader5.COPY_TICKS_ALL
			)
		return self.serializers.records.tick.to_dataframe(
			records,
			name = chart.name,
			select = chart.select,
			tz = self.timezone,
		)

	def read_raw_candlestick_chart(self, chart: CandleStickChart):
		if chart.count:
			records = MetaTrader5.copy_rates_from(
				chart.symbol,
				self.serializers.interval.serialize(chart.interval),
				chart.to_timestamp.to_pydatetime(),
				chart.count
			)
		else:
			records = MetaTrader5.copy_rates_range(
				chart.symbol,
				self.serializers.interval.serialize(chart.interval),
				chart.from_timestamp.to_pydatetime(),
				chart.to_timestamp.to_pydatetime(),
			)
		return self.serializers.records.candlestick.to_dataframe(
			records,
			name = chart.name,
			select = chart.select,
			tz = self.timezone,
		)

	def ensure_interval_integrity(
		self,
		dataframe: pandas.DataFrame = None,
		chart: OverriddenChart = None,
		frequency_tolerance: int = 50,
	):
		if not (chart.from_timestamp and chart.to_timestamp and chart.interval):
			return dataframe # Not enough data to do an interval integrity 

		if len(dataframe) == 0:
			return dataframe

		try:
			average_frequency = numpy.diff(dataframe.index.to_numpy()).mean()
			expected_frequency = chart.interval.to_pandas_timedelta()
			if average_frequency / expected_frequency > frequency_tolerance:
				logger.warn(f"Missing too many data points. It's likely that MetaTrader attempted to compensate for less granularity by returning a higher granular data. Skipping results...\nAverage Frequency of Received Data: {average_frequency}\nExpected Frequency: {expected_frequency}")
				return self.serializers.records.candlestick.to_dataframe(
					[],
					name = chart.name,
					select = chart.select,
					tz = self.timezone,
				)
		except:
			pass
		return dataframe

	def get_last_price(
		self,
		symbol: Symbol,
		timestamp: pandas.Timestamp = None,
		intent: 'OrderType' = None
	) -> float:
		if timestamp:
			chart = TickChart(
				symbol = symbol,
				to_timestamp = timestamp,
				count = 1,
				repository = self,
			).read()

			bid = chart.data['bid'].iloc[0]
			ask = chart.data['ask'].iloc[0]
		else:
			symbol_info = MetaTrader5.symbol_info(symbol)
			if not symbol_info:
				return None
			bid = symbol_info.bid
			ask = symbol_info.ask

		if intent == 'buy':
			return ask
		if intent == 'sell':
			return bid

		return (bid + ask) / 2

	def get_spread(self, symbol):
		return MetaTrader5.symbol_info(symbol).spread

	def get_point_size(self, symbol):
		return MetaTrader5.symbol_info(symbol).point

	def get_base_currency(self, symbol):
		return MetaTrader5.symbol_info(symbol).currency_base

	def get_quote_currency(self, symbol):
		return MetaTrader5.symbol_info(symbol).currency_profit