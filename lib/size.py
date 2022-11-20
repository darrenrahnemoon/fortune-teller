class Size:
	@staticmethod
	def Lot(lot: float):
		return lot * 100000

	@staticmethod
	def MiniLot(mini_lot: float):
		return mini_lot * 10000

	@staticmethod
	def Units(units: float):
		return units

	@staticmethod
	def PercentageOfBalance(percentage: float):
		return lambda order: order.broker.balance * percentage / 100

	@staticmethod
	def PercentageRiskManagement(percentage: float):
		return lambda order: percentage * order.broker.balance / abs(order.sl - order.broker.get_last_price(order.symbol)) / 10 * 100000

	@staticmethod
	def FixedRiskManagement(amount: float):
		return lambda order: amount / abs(order.sl - order.broker.get_last_price(order.symbol)) / 10 * 100000
