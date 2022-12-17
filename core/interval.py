import numpy
import pandas
import typing

if typing.TYPE_CHECKING:
	from core.broker import Broker

class Interval:
	multiplier: float = 1

	pandas_timedelta_unit: str = None
	pandas_frequency_unit: str = None
	numpy_timedelta_unit: str = None

	# --- Just for easy access ---
	Millisecond: type['Interval'] = None
	Second: type['Interval'] = None
	Minute: type['Interval'] = None
	Hour: type['Interval'] = None
	Day: type['Interval'] = None
	Week: type['Interval'] = None
	Month: type['Interval'] = None
	Quarter: type['Interval'] = None
	Year: type['Interval'] = None
	# ----------------------------

	def __init__(self, amount: float) -> None:
		self._amount = amount
		self._pandas_timedelta = pandas.Timedelta(self._real_amount, self.pandas_timedelta_unit)

	def __hash__(self) -> int:
		return hash((self._real_amount, self.unit))

	def __repr__(self) -> str:
		return f'{self.unit}({self._amount})'

	def _normalize_other(self, other):
		return other._pandas_timedelta if isinstance(other, Interval) else other

	def __eq__(self, other) -> bool:
		return self._pandas_timedelta == self._normalize_other(other)

	def __lt__(self, other):
		return self._pandas_timedelta < self._normalize_other(other)

	def __lte__(self, other):
		return self.__eq__(other) or self.__lt__(other)

	def __gt__(self, other):
		return not self.__lt__(other)

	def __gte__(self, other):
		return self.__eq__(other) or self.__gt__(other)

	@property
	def _real_amount(self):
		return self._amount * self.multiplier

	@property
	def unit(self):
		return type(self).__name__

	def to_pandas_timedelta(self) -> pandas.Timedelta:
		return self._pandas_timedelta

	def to_pandas_frequency(self) -> str:
		return f'{self._real_amount}{self.pandas_frequency_unit}'

	def to_numpy_timedelta(self) -> str:
		return numpy.timedelta64(self._real_amount, self.numpy_timedelta_unit)


class Millisecond(Interval):
	pandas_timedelta_unit='milliseconds'
	pandas_frequency_unit='ms'
	numpy_timedelta_unit = 'ms'
Interval.Millisecond = Millisecond

class Second(Interval):
	pandas_timedelta_unit = 'seconds'
	pandas_frequency_unit = 'S'
	numpy_timedelta_unit = 's'
Interval.Second = Second

class Minute(Interval):
	pandas_timedelta_unit = 'minutes'
	pandas_frequency_unit = 'T'
	numpy_timedelta_unit = 'm'
Interval.Minute = Minute

class Hour(Interval):
	pandas_timedelta_unit = 'hours'
	pandas_frequency_unit = 'H'
	numpy_timedelta_unit = 'h'
Interval.Hour = Hour

class Day(Interval):
	pandas_timedelta_unit = 'days'
	pandas_frequency_unit = 'D'
	numpy_timedelta_unit = 'D'
Interval.Day = Day

class Week(Interval):
	pandas_timedelta_unit = 'W'
	pandas_frequency_unit = 'W'
	numpy_timedelta_unit = 'W'
Interval.Week = Week

# Pandas/Numpy and others don't have a definition for month as its amount is variable depending on the month so we naively assume 30 days 
class Month(Day):
	multiplier = 30
Interval.Month = Month

class Quarter(Month):
	multiplier = 3
Interval.Quarter = Quarter

class Year(Day):
	multiplier = 365
Interval.Year = Year
