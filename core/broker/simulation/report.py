import typing
import numpy
import pandas
import functools
import operator
from dataclasses import dataclass

if typing.TYPE_CHECKING:
	from core.strategy import Strategy
from core.order import Order
from core.position import Position

from core.utils.time import TimeWindow, now

@dataclass
class TimestepsReport(TimeWindow):
	sample: list[pandas.Timestamp] = None

	@classmethod
	def from_timesteps(cls, timesteps: pandas.Series):
		report = cls()
		report.from_timestamp = timesteps[0]
		report.to_timestamp = timesteps[-1]
		report.sample = list(timesteps[:5]) + [ None ] + list(timesteps[-5:])
		return report

@dataclass
class EquityReport:
	open: float = None
	high: float = None
	low: float = None
	close: float = None

	curve: pandas.Series = None
	max_drawdown_percentage: float = None
	return_percentage: float = None

	@classmethod
	def from_curve(cls, equity_curve: pandas.Series) -> None:
		report = cls()
		report.open = equity_curve[0]
		report.high = equity_curve.max()
		report.low = equity_curve.min()
		report.close = equity_curve[-1]
		report.curve = equity_curve
		report.max_drawdown_percentage = max(1 - equity_curve / numpy.maximum.accumulate(equity_curve))
		report.return_percentage = report.open / report.close * 100 - 100
		return report

@dataclass
class NumericStats:
	min: float = None
	max: float = None
	average: float = None

	@classmethod
	def from_collection(cls, collection: list, key: str = None):
		items = [ getattr(item, key) for item in collection if getattr(item, key) != None ] if key else collection
		stats = cls()
		stats.min = min(items)
		stats.max = max(items)
		stats.average = functools.reduce(operator.add, items) / len(items)
		return stats

@dataclass
class OrdersReport:
	history: list[Order] = None
	duration: NumericStats = None

	@classmethod
	def from_orders(cls, orders: list[Order]) -> None:
		report = cls()
		report.history = orders
		report.duration = NumericStats.from_collection(orders, 'duration')
		return report

@dataclass
class PositionsReport:
	history: list[Position] = None
	duration: NumericStats = None
	profit: NumericStats = None
	win_rate: float = None

	@classmethod
	def from_positions(cls, positions: list[Position]) -> None:
		report = cls()
		report.history = positions
		report.duration = NumericStats.from_collection(positions, 'duration')
		report.profit = NumericStats.from_collection(positions, 'profit')
		report.win_rate = len([ position for position in positions if position.is_in_profit ]) / len(positions) * 100
		return report

@dataclass
class BacktestReport:
	created_at: pandas.Timestamp = None
	strategy: 'Strategy' = None
	timesteps: TimestepsReport = None
	equity: EquityReport = None
	orders: OrdersReport = None
	positions: PositionsReport = None

	@classmethod
	def from_strategy(cls, strategy: 'Strategy'):
		report = cls()
		report.created_at = now()
		report.strategy = strategy
		report.timesteps = TimestepsReport.from_timesteps(strategy.broker.timesteps)
		report.equity = EquityReport.from_curve(strategy.broker.equity_curve)
		report.orders = OrdersReport.from_orders(strategy.broker.orders)
		report.positions = PositionsReport.from_positions(strategy.broker.positions)
		return report