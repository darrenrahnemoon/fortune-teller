import numpy
import pandas
from lib.interval import Interval
from lib.utils.test import it, describe
from lib.broker import MetaTraderBroker

@describe('Interval')
def _():

	@it('should implicitly assume interval classes and interval instances of amount 1 are equal')
	def _():
		assert Interval.Day(2) != Interval.Month(2)

	@it('should return the correct timedelta given an interval')
	def _():
		assert Interval.Day(2).to_pandas_timedelta() == pandas.Timedelta(2, 'day')
		assert Interval.Hour(1).to_pandas_timedelta() == pandas.Timedelta(1, 'H')
		assert Interval.Week(1).to_numpy_timedelta() == numpy.timedelta64(1, 'W')
		assert Interval.Year(5).to_numpy_timedelta() == numpy.timedelta64(5, 'Y')
		assert Interval.Month(3).to_numpy_timedelta() == numpy.timedelta64(90, 'D')

	@it('should get the correct broker-specific interval')
	def _():
		assert Interval.Minute(1).to_broker(MetaTraderBroker) == 1
		assert Interval.Minute(5).to_broker(MetaTraderBroker) == 5
		assert Interval.Week(1).to_broker(MetaTraderBroker) == 1 | 0x8000