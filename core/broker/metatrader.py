import pandas
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from core.chart import TickChart
from core.repository import MetaTraderRepository
from core.broker.broker import Broker
if TYPE_CHECKING:
	from core.chart import Symbol

@dataclass
class MetaTraderBroker(Broker):
	repository: MetaTraderRepository = field(default_factory = MetaTraderRepository)

	def get_last_price(
		self,
		symbol: 'Symbol',
		timestamp: pandas.Timestamp = None
	) -> float:
		if timestamp:
			chart = TickChart(
				symbol = symbol,
				to_timestamp = timestamp,
				count = 1,
				repository = self.repository,
			).read()
			return (chart.data['bid'].iloc[0] + chart.data['ask'].iloc[0]) / 2

		symbol_info = self.repository.api.symbol_info(symbol)
		return (symbol_info.ask + symbol_info.bid) / 2