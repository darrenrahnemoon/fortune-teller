import numpy
import pandas
import typing

if typing.TYPE_CHECKING:
	from lib.broker import Broker

class Interval:
	amount: float = 1
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

	def __init__(self, amount: float = 1) -> None:
		self.amount = amount

	def __hash__(self) -> int:
		return hash((self.real_amount, self.unit))

	def __repr__(self) -> str:
		return f'{self.unit}({self.amount})'

	def __eq__(self, other: object) -> bool:
		if not isinstance(other, Interval):
			return False
		return self.amount == other.amount and self.unit == other.unit

	@property
	def real_amount(self):
		return self.amount * self.multiplier

	@property
	def unit(self):
		return type(self).__name__

	@property
	def to_pandas_timedelta(self) -> pandas.Timedelta:
		return pandas.Timedelta(self.real_amount, self.pandas_timedelta_unit)

	@property
	def to_pandas_frequency(self) -> str:
		return f'{self.real_amount}{self.pandas_frequency_unit}'

	@property
	def to_numpy_timedelta(self) -> str:
		return numpy.timedelta64(self.real_amount, self.numpy_timedelta_unit)

	def to_broker(self, broker: type['Broker'] or 'Broker' = None):
		return broker.intervals[self]

class Millisecond(Interval):
	pandas_timedelta_unit='ms'
	pandas_frequency_unit='ms'
	numpy_timedelta_unit = 'ms'
Interval.Millisecond = Millisecond

class Second(Interval):
	pandas_timedelta_unit = 'second'
	pandas_frequency_unit = 'S'
	numpy_timedelta_unit = 's'
Interval.Second = Second

class Minute(Interval):
	pandas_timedelta_unit = 'minute'
	pandas_frequency_unit = 'T'
	numpy_timedelta_unit = 'm'
Interval.Minute = Minute

class Hour(Interval):
	pandas_timedelta_unit = 'H'
	pandas_frequency_unit = 'H'
	numpy_timedelta_unit = 'h'
Interval.Hour = Hour

class Day(Interval):
	pandas_timedelta_unit = 'day'
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

class Year(Interval):
	pandas_timedelta_unit = 'year'
	pandas_frequency_unit = 'Y'
	numpy_timedelta_unit = 'Y'
Interval.Year = Year
