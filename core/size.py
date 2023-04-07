from abc import abstractmethod
from functools import cached_property
from typing import TYPE_CHECKING, ClassVar
from dataclasses import dataclass

if TYPE_CHECKING:
	from core.order import Order

@dataclass
class Size:
	value: float
	order: 'Order' = None

	# --- Just for easy access ---
	Lot: ClassVar[type['Size']] = None
	MiniLot: ClassVar[type['Size']] = None
	Unit: ClassVar[type['Size']] = None
	PercentageOfBalance: ClassVar[type['Size']] = None
	PercentageOfBalanceRiskManagement: ClassVar[type['Size']] = None
	FixedAmountRiskManagement: ClassVar[type['Size']] = None
	# ----------------------------

	def __init__(self, value: float or int) -> None:
		self.value = value

	@abstractmethod
	def from_units(self, units: int):
		pass

	@abstractmethod
	def to_units(self):
		pass

	def to(self, size_class: type['Size']):
		units = self.to_units()
		size = size_class(value = 0, order = self.order)
		size.from_units(units)
		return size

@dataclass
class Lot(Size):
	def from_units(self, units: int):
		self.value = units / self.order.broker.get_units_in_one_lot(self.order.symbol)

	def to_units(self):
		return self.value * self.order.broker.get_units_in_one_lot(self.order.symbol)

Size.Lot = Lot

@dataclass
class MiniLot(Lot):
	def from_units(self, units: int):
		super().from_units(units)
		self.value = self.value / 10

	def to_units(self):
		return super().to_units() * 10

Size.MiniLot = MiniLot

@dataclass
class Unit(Size):
	def from_units(self, units: int):
		self.value = units

	def to_units(self):
		return self.value

Size.Unit = Unit

@dataclass
class FixedAmountRiskManagement(Size):
	def from_units(self, units: int):
		raise NotImplemented()

	def to_units(self):
		risk_amount = self.order.broker.repository.convert_currency(
			amount = self.value,
			from_currency = self.order.broker.currency,
			to_currency = self.order.broker.repository.get_quote_currency(self.order.symbol),
		) # In instrument's currency
		last_price = self.order.broker.repository.get_last_price(
			symbol = self.order.symbol,
			intent = self.order.type
		) # Instrument's last price
		return risk_amount / last_price

Size.FixedAmountRiskManagement = FixedAmountRiskManagement

@dataclass
class PercentageOfBalance(Size):
	def from_units(self, units: int):
		raise NotImplemented()

	def to_units(self):
		risk_amount = self.order.broker.balance * self.value # In broker's base currency
		risk_amount = self.order.broker.repository.convert_currency(
			amount = risk_amount,
			from_currency = self.order.broker.currency,
			to_currency = self.order.broker.repository.get_quote_currency(self.order.symbol),
		) # In instrument's currency
		last_price = self.order.broker.repository.get_last_price(
			symbol = self.order.symbol,
			intent = self.order.type
		)
		return risk_amount / last_price

Size.PercentageOfBalance = PercentageOfBalance

@dataclass
class PercentageOfBalanceRiskManagement(Size):
	def from_units(self, units: int):
		raise NotImplemented()

	def to_units(self):
		risk_amount = self.order.broker.balance * self.value # In broker's base currency
		risk_amount = self.order.broker.repository.convert_currency(
			amount = risk_amount,
			from_currency = self.order.broker.currency,
			to_currency = self.order.broker.repository.get_quote_currency(self.order.symbol),
		) # In instrument's currency
		risk_amount_per_pip = risk_amount / self.pips_at_risk
		return risk_amount_per_pip * self.pip_value

	@cached_property
	def pip_value(self):
		symbol = self.order.symbol
		amount = self.order.broker.repository.get_pip_size(symbol) * self.order.broker.get_units_in_one_lot(symbol)
		return self.order.broker.repository.convert_currency(
			amount = amount,
			from_currency = self.order.broker.repository.get_quote_currency(symbol),
			to_currency = self.order.broker.currency
		)

	@cached_property
	def pips_at_risk(self):
		symbol = self.order.symbol
		last_price = self.order.broker.repository.get_last_price(
			symbol = symbol,
			intent = self.order.type
		)
		pip_size = self.order.broker.repository.get_pip_size(symbol)
		return abs(self.order.sl - last_price) / pip_size

Size.PercentageOfBalanceRiskManagement = PercentageOfBalanceRiskManagement
