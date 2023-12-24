from dataclasses import dataclass

from core.trading.chart.chart import Chart
from core.trading.interval import Interval

@dataclass
class LineChart(Chart):
	@dataclass
	class Query(Chart.Query):
		interval: Interval = None
		maturity: Interval = None

	@dataclass
	class Record(Chart.Record):
		value: float = None

	interval: Interval = None
	maturity: Interval = None