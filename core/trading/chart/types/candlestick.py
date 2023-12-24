from dataclasses import dataclass

from core.trading.chart.chart import Chart
from core.trading.interval import Interval

@dataclass
class CandleStickChart(Chart):
	interval: Interval = None

	@dataclass
	class Query(Chart.Query):
		interval: Interval = None

	@dataclass
	class Record(Chart.Record):
		open: float = None
		high: float = None
		low: float = None
		close: float = None
		volume_tick: float = None
		volume_real: float = None
		spread_pips: float = None
