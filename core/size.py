from functools import cached_property
from typing import TYPE_CHECKING, ClassVar
from dataclasses import dataclass

if TYPE_CHECKING:
	from core.order import Order

@dataclass
class Size:
	value: float
	units = 1

	# --- Just for easy access ---
	Lot: ClassVar[type['Size']] = None
	MiniLot: ClassVar[type['Size']] = None
	Unit: ClassVar[type['Size']] = None
	PercentageOfBalance: ClassVar[type['OrderDependantSize']] = None
	PercentageOfBalanceRiskManagement: ClassVar[type['OrderDependantSize']] = None
	FixedAmountRiskManagement: ClassVar[type['OrderDependantSize']] = None
	# ----------------------------

	def __init__(self, value: float or int) -> None:
		self.value = value

	@cached_property
	def to_units(self):
		return self.value * self.units

	def to(self, other_size: type['Size']):
		return self.to_units / other_size.units

class Lot(Size):
	units = 100000
Size.Lot = Lot

class MiniLot(Size):
	units = 10000
Size.MiniLot = MiniLot

class Unit(Size):
	units = 1
Size.Unit = Unit

@dataclass
class OrderDependantSize(Size):
	order: 'Order' = None

	@property
	def broker(self):
		return self.order.broker

	@property
	def repository(self):
		return self.broker.repository

	@cached_property
	def pips_at_risk(self):
		symbol = self.order.symbol
		sl = self.order.sl
		last_price = self.repository.get_last_price(
			symbol = symbol,
			intent = self.order.type
		)
		pip_size = self.repository.get_pip_size(symbol)
		return abs(sl - last_price) / pip_size

	@cached_property
	def pip_value(self):
		symbol = self.order.symbol
		return self.repository.convert_currency(
			amount = self.repository.get_pip_size(symbol) * self.broker.standard_size.units,
			from_currency = self.repository.get_quote_currency(symbol),
			to_currency = self.broker.currency
		)

@dataclass
class PercentageOfBalance(OrderDependantSize):
	units = 1

	@cached_property
	def to_units(self):
		risk_amount = self.order.broker.balance * self.value # In broker's base currency
		risk_amount = self.repository.convert_currency(
			amount = risk_amount,
			from_currency = self.order.broker.currency,
			to_currency = self.repository.get_quote_currency(self.order.symbol),
		)

		return risk_amount / self.repository.get_last_price(
			symbol = self.order.symbol,
			intent = self.order.type
		)

Size.PercentageOfBalance = PercentageOfBalance

@dataclass
class PercentageOfBalanceRiskManagement(OrderDependantSize):
	units = 1
	result: float = None

	@cached_property
	def to_units(self):
		risk_amount = self.order.broker.balance * self.value # In broker's base currency
		risk_amount = self.repository.convert_currency(
			amount = risk_amount,
			from_currency = self.order.broker.currency,
			to_currency = self.repository.get_quote_currency(self.order.symbol),
		)
		risk_amount_per_pip = risk_amount / self.pips_at_risk

		return risk_amount_per_pip * self.pip_value

Size.PercentageOfBalanceRiskManagement = PercentageOfBalanceRiskManagement

@dataclass
class FixedAmountRiskManagement(OrderDependantSize):
	units = 1
	result: float = 0

	@cached_property
	def to_units(self):
		risk_amount = self.repository.convert_currency(
			amount = self.value,
			from_currency = self.order.broker.currency,
			to_currency = self.repository.get_quote_currency(self.order.symbol),
		)

		return risk_amount / self.repository.get_last_price(
			symbol = self.order.symbol,
			intent = self.order.type
		)

Size.FixedAmountRiskManagement = FixedAmountRiskManagement
