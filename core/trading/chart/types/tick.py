from dataclasses import dataclass
from core.trading.chart.chart import Chart

@dataclass
class TickChart(Chart):
	@dataclass
	class Record(Chart.Record):
		bid: float = None
		ask: float = None
		last: float = None
		volume_tick: float = None
		volume_real: float = None
