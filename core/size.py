import typing
from dataclasses import dataclass

if typing.TYPE_CHECKING:
	from core.order import Order

@dataclass
class Size:
	value: float
	units: float = 1

	# --- Just for easy access ---
	Lot: typing.ClassVar[type['Size']] = None
	MiniLot: typing.ClassVar[type['Size']] = None
	Unit: typing.ClassVar[type['Size']] = None
	PercentageOfBalance: typing.ClassVar[type['Size']] = None
	RiskManagedPercentageOfBalance: typing.ClassVar[type['Size']] = None
	FixedRiskManagement: typing.ClassVar[type['Size']] = None
	# ----------------------------

	def __init__(self, value: float or int) -> None:
		self.value = value

	def to_units(self, *args, **kwargs):
		return self.value * self.units

	def to(self, other_size: type['Size'], *args, **kwargs):
		return self.to_units(*args, **kwargs) / other_size.units

class Lot(Size):
	units = 100000
Size.Lot = Lot

class MiniLot(Size):
	units = 10000
Size.MiniLot = MiniLot

class Unit(Size):
	units = 1
Size.Unit = Unit

class PercentageOfBalance(Size):
	units = None # Cannot convert sizes to PercentageOfBalance
	def to_units(self, order: 'Order'):
		cash_amount = order.broker.balance * self.value
		unit_amount = order.broker.get_last_price(order.symbol)
		return cash_amount // unit_amount

Size.PercentageOfBalance = PercentageOfBalance

class RiskManagedPercentageOfBalance(Size):
	units = None # Cannot convert sizes to RiskManagedPercentageOfBalance
	def to_units(self, order: 'Order'):
		cash_amount = order.broker.balance * self.value
		sl_diff = abs(order.sl - order.broker.get_last_price(order.symbol))
		return cash_amount / sl_diff * 10000

Size.RiskManagedPercentageOfBalance = RiskManagedPercentageOfBalance

class FixedRiskManagement(Size):
	units = None # Cannot convert sizes to FixedRiskManagement
	def to_units(self, order: 'Order'):
		sl_diff = abs(order.sl - order.broker.get_last_price(order.symbol))
		return  self.value / sl_diff * 10000

Size.FixedRiskManagement = FixedRiskManagement
