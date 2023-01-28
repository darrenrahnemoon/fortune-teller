from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from core.repository import MetaTraderRepository
from core.broker.broker import Broker
if TYPE_CHECKING:
	from core.chart import Symbol

@dataclass
class MetaTraderBroker(Broker):
	repository: MetaTraderRepository = field(default_factory = MetaTraderRepository)

	def get_last_price(self, symbol: 'Symbol') -> float:
		symbol_info = self.repository.api.symbol_info(symbol)
		return (symbol_info.ask + symbol_info.bid) / 2