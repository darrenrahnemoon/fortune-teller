import numpy
import pandas
from core.trading.interval import Interval
from core.utils.test import test

@test.group('Interval')
def _():

	@test.case('should implicitly assume interval classes and interval instances of amount 1 are equal')
	def _():
		assert Interval.Day(2) != Interval.Month(2)

	@test.case('should return the correct timedelta given an interval')
	def _():
		assert Interval.Day(2).to_pandas_timedelta() == pandas.Timedelta(2, 'day')
		assert Interval.Hour(1).to_pandas_timedelta() == pandas.Timedelta(1, 'H')
		assert Interval.Week(1).to_numpy_timedelta() == numpy.timedelta64(1, 'W')
		assert Interval.Year(5).to_numpy_timedelta() == numpy.timedelta64(5 * 365, 'D')
		assert Interval.Month(3).to_numpy_timedelta() == numpy.timedelta64(90, 'D')
