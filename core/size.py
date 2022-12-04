import typing
from dataclasses import dataclass

if typing.TYPE_CHECKING:
	from core.order import Order

@dataclass
class Size:
	value: float
 
	# --- Just for easy access ---
	Lot: typing.ClassVar[type['Size']] = None
	MiniLot: typing.ClassVar[type['Size']] = None
	Units: typing.ClassVar[type['Size']] = None
	PercentageOfBalance: typing.ClassVar[type['Size']] = None
	PercentageRiskManagement: typing.ClassVar[type['Size']] = None
	FixedRiskManagement: typing.ClassVar[type['Size']] = None
	# ----------------------------

	def __init__(self, value: float) -> None:
		self.value = value

	def to_units(self, order: 'Order'):
		pass

class Lot(Size):
	def to_units(self, order: 'Order'):
		return self.value * 100000
Size.Lot = Lot

class MiniLot(Size):
	def to_units(self, order: 'Order'):
		return self.value * 10000
Size.MiniLot = MiniLot

class Units(Size):
	def to_units(self, order: 'Order'):
		return self.value
Size.Units = Units

class PercentageOfBalance(Size):
	def to_units(self, order: 'Order'):
		return order.broker.balance * self.value / 100
Size.PercentageOfBalance = PercentageOfBalance

class PercentageRiskManagement(Size):
	def to_units(self, order: 'Order'):
		return self.value * order.broker.balance / abs(order.sl - order.broker.get_last_price(order.symbol)) / 10 * 100000
Size.PercentageRiskManagement = PercentageRiskManagement

class FixedRiskManagement(Size):
	def to_units(self, order: 'Order'):
		return self.value / abs(order.sl - order.broker.get_last_price(order.symbol)) / 10 * 100000
Size.FixedRiskManagement = FixedRiskManagement
