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

	@cached_property
	def broker_base_currency_exchange_rate(self) -> float:
		"""In broker's base currency / instrument's quote currency"""
		instrument_quote_currency = self.order.broker.repository.get_quote_currency(self.order.symbol)
		if instrument_quote_currency == self.order.broker.base_currency:
			return 1

		exchange_rate = self.order.broker.get_last_price(f'{instrument_quote_currency}{self.order.broker.base_currency}')
		if exchange_rate:
			return exchange_rate

		# Try the inverse pair if we couldn't get a quote
		exchange_rate = self.order.broker.get_last_price(f'{self.order.broker.base_currency}{instrument_quote_currency}')
		if exchange_rate:
			return 1 / exchange_rate

		raise Exception(f"Cannot calculate the exchange rate for '{instrument_quote_currency}{self.order.broker.base_currency}'")

	@cached_property
	def risk_per_unit(self):
		"""In instrument's quote currency"""
		return abs(self.order.sl - self.order.broker.get_last_price(self.order.symbol))

@dataclass
class PercentageOfBalance(OrderDependantSize):
	units = 1

	@cached_property
	def to_units(self):
		amount = self.order.broker.balance * self.value # In broker's base currency
		amount = amount / self.broker_base_currency_exchange_rate # In instrument's quote currency
		return amount / self.order.broker.get_last_price(self.order.symbol) # In units

Size.PercentageOfBalance = PercentageOfBalance

@dataclass
class PercentageOfBalanceRiskManagement(OrderDependantSize):
	units = 1
	result: float = None

	@cached_property
	def to_units(self):
		amount = self.order.broker.balance * self.value # In broker's base currency
		risk_per_unit = self.risk_per_unit * self.broker_base_currency_exchange_rate # In broker's base currency
		return amount / risk_per_unit # In units

Size.PercentageOfBalanceRiskManagement = PercentageOfBalanceRiskManagement

@dataclass
class FixedAmountRiskManagement(OrderDependantSize):
	units = 1
	result: float = 0

	@cached_property
	def to_units(self):
		risk_per_unit = self.risk_per_unit * self.broker_base_currency_exchange_rate # In broker's base currency
		return self.value / risk_per_unit

Size.FixedAmountRiskManagement = FixedAmountRiskManagement
