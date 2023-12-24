import pandas
from abc import abstractmethod
from typing import TYPE_CHECKING, ClassVar, Iterable
from dataclasses import dataclass
if TYPE_CHECKING:
	from core.trading.chart import Chart, Symbol
	from core.trading.order import OrderType

from core.utils.time import now
from core.utils.collection import ensure_list, is_any_of

ChartCombinations = dict[
	type['Chart'], dict[str, list]
]

@dataclass
class Repository:
	timezone: ClassVar[str] = 'UTC'

	@property
	def now(self):
		return now(self.timezone)

	def get_available_symbols(self):
		symbols = set()
		for chart in self.get_filtered_charts():
			symbols.add(chart.symbol)
		return list(symbols)

	@abstractmethod
	def get_charts(self, **kwargs) -> Iterable['Chart']:
		"""lists out all available chart combinations for this repository"""
		pass

	def get_filtered_charts(
		self,
		filter: dict[str] = {},
		**kwargs,
	) -> Iterable['Chart']:
		"""similar to get_charts but with the ability to filter charts

		Args:
			filter (dict[str], optional): filter dict. Defaults to {}.

		Yields:
			Iterable['Chart']: iterable of charts with filter applied
		"""
		charts = self.get_charts(**kwargs)
		for chart in charts:
			exclude = False
			for field_name, filter_values in filter.items():
				if filter_values == None:
					continue

				filter_values = ensure_list(filter_values)
				if len(filter_values) == 0:
					continue

				if not is_any_of(filter_values, lambda filter_value: filter_value == getattr(chart, field_name, None)):
					exclude = True

			if not exclude:
				yield chart

	@abstractmethod
	def read_chart(
		self,
		chart: 'Chart' = None,
		**overrides
	) -> pandas.DataFrame:
		pass

	@abstractmethod
	def get_last_price(
		self,
		symbol: 'Symbol',
		timestamp: pandas.Timestamp = None,
		intent: 'OrderType' = None
	) -> float:
		pass

	@abstractmethod
	def write_chart(
		self,
		chart: 'Chart' = None,
		**overrides
	) -> None:
		pass

	def convert_currency(
		self,
		amount,
		from_currency: str,
		to_currency: str,
		timestamp: pandas.Timestamp = None,
	):
		if from_currency == to_currency:
			return amount

		exchange_rate = self.get_last_price(
			symbol = f'{from_currency}{to_currency}',
			timestamp = timestamp,
		)
		if exchange_rate != None:
			return amount * exchange_rate

		exchange_rate = self.get_last_price(
			symbol = f'{to_currency}{from_currency}',
			timestamp = timestamp,
		)
		if exchange_rate != None:
			return amount / exchange_rate

		raise Exception(f"Cannot calculate the exchange rate from {from_currency} to {to_currency}'")


	@abstractmethod
	def get_spread(self, symbol: 'Symbol') -> int:
		pass

	@abstractmethod
	def get_pip_size(self, symbol: 'Symbol'):
		return self.get_point_size(symbol) * 10

	@abstractmethod
	def get_point_size(self, symbol: 'Symbol'):
		pass

	@abstractmethod
	def get_base_currency(self, symbol: 'Symbol'):
		pass

	@abstractmethod
	def get_quote_currency(self, symbol: 'Symbol'):
		pass
