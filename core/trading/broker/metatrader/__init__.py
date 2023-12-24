import core.trading.repository.metatrader.resolve

import pandas
import MetaTrader5
from dataclasses import dataclass, field
from typing import Iterable, TYPE_CHECKING

from core.trading.broker.metatrader.errors import PositionError, OrderError
from core.trading.position import Position, PositionStatus, PositionType
from core.trading.order import Order, OrderStatus, OrderType
from core.trading.repository import MetaTraderRepository
from core.trading.broker.broker import Broker
from core.trading.broker.metatrader.serializers import MetaTraderSerializers

if TYPE_CHECKING:
	from core.trading.chart import Symbol
from core.trading.size import Size
from core.utils.time import TimestampLike
from core.utils.logging import Logger

logger = Logger(__name__)

@dataclass
class MetaTraderBroker(Broker):
	id = 6969
	serializers = MetaTraderSerializers()
	repository: MetaTraderRepository = field(default_factory = MetaTraderRepository)

	def get_orders(
		self,
		symbol: 'Symbol' = None,
		type: OrderType = None,
		from_timestamp: TimestampLike = None,
		to_timestamp: TimestampLike = None,
		status: OrderStatus = 'open',
	) -> Iterable[Order]:
		if status == 'open':
			orders = MetaTrader5.orders_get(symbol = symbol)
		else:
			orders = MetaTrader5.history_orders_get(
				(from_timestamp or pandas.Timestamp(0, tz = 'UTC')).to_pydatetime(),
				(to_timestamp or self.now).to_pydatetime(),
			)

		if orders == None:
			raise OrderError(
				message = 'Failed to get orders.',
				response = orders
			)

		for order in orders:
			order = self.serializers.order.to_order(order)
			if symbol and order.symbol != symbol:
				continue

			if status and order.status != status:
				continue

			if type and order.type != type:
				continue

			if from_timestamp and order.open_timestamp < from_timestamp:
				continue

			if to_timestamp and order.open_timestamp > to_timestamp:
				continue

			order.broker = self
			yield order

	def place_order(self, order: Order, comment = '', **kwargs) -> Order:
		request = dict(
			action = self.serializers.order.to_metatrader_action(order),
			symbol = order.symbol,
			volume = self.serializers.order.to_metatrader_size(order.size),
			type = self.serializers.order.to_metatrader_type(order),
			magic = self.id,
			type_filling = MetaTrader5.ORDER_FILLING_IOC,
			comment = comment
		)

		if order.stop:
			request['stoplimit'] = float(order.stop)
		if order.limit:
			request['price'] = float(order.limit)
		if order.sl:
			request['sl'] = float(order.sl)
		if order.tp: 
			request['tp'] = float(order.tp)

		response = MetaTrader5.order_send(request)
		logger.debug(f'Place Order Response:\n{response}')

		if response == None or response.retcode != MetaTrader5.TRADE_RETCODE_DONE:
			raise OrderError(
				message = 'Failed to place order.',
				request = request,
				response = response,
				order = order,
			)
		else:
			order.status = 'placed'
			order.id = response.order
			order.open_timestamp = self.now

		return order

	def cancel_order(self, order: Order) -> Order:
		request = dict(
			action = MetaTrader5.TRADE_ACTION_REMOVE,
			order = order.id
		)
		response = MetaTrader5.order_send(request)
		logger.debug(f'Cancel Order Response:\n{response}')

		if response == None or response.retcode != MetaTrader5.TRADE_RETCODE_DONE:
			raise OrderError(
				message = 'Failed to cancel order.',
				order = order,
				request = request,
				response = response
			)
		else:
			order.status = 'canceled'
			order.close_timestamp = self.now

		return order

	def get_positions(
		self,
		symbol: 'Symbol' = None,
		type: PositionType = None,
		from_timestamp: TimestampLike = None,
		to_timestamp: TimestampLike = None,
		status: PositionStatus = 'open',
	) -> Iterable[Position]:
		if status == 'open':
			positions = MetaTrader5.positions_get(symbol = symbol)
		else:
			raise PositionError('Getting `closed` positions is currently not supported by MetaTraderBroker')
		for position in positions:
			position = self.serializers.position.to_position(position)

			if status and position.status != status:
				continue

			if type and position.type != type:
				continue

			if from_timestamp and position.open_timestamp < from_timestamp:
				continue

			if to_timestamp and position.open_timestamp > to_timestamp:
				continue

			position.broker = self
			yield position

	def modify_position(self, position: Position):
		request = dict(
			action = MetaTrader5.TRADE_ACTION_SLTP,
			position = position.id,
			sl = position.sl,
			tp = position.tp,
		)
		response = MetaTrader5.order_send(request)
		if response == None or response.retcode != MetaTrader5.TRADE_RETCODE_DONE:
			raise PositionError(
				message = 'Failed to modify position',
				position = position,
				request = request,
				response = response
			)

	def close_position(self, position: Position):
		request = dict(
			action = MetaTrader5.TRADE_ACTION_DEAL,
			symbol = position.symbol,
			type = MetaTrader5.ORDER_TYPE_SELL if position.type == 'buy' else MetaTrader5.ORDER_TYPE_BUY,
			volume = self.serializers.order.to_metatrader_size(position.size),
			position = position.id,
			magic = self.id,
			type_filling = MetaTrader5.ORDER_FILLING_IOC,
		)

		response = MetaTrader5.order_send(request)
		logger.debug(f'Close Position Response:\n{response}')
		if response == None or response.retcode != MetaTrader5.TRADE_RETCODE_DONE:
			raise PositionError(
				message = 'Failed to close position',
				position = position,
				request = request,
				response = response
			)
		else:
			position.exit_price = response.price
			position.status = 'closed'
			position.close_timestamp = self.now

		return position

	@property
	def balance(self) -> float:
		return MetaTrader5.account_info().balance

	@property
	def equity(self) -> float:
		return MetaTrader5.account_info().equity

	@property
	def currency(self) -> str:
		return MetaTrader5.account_info().currency

	def get_units_in_one_lot(self, symbol: 'Symbol'):
		return MetaTrader5.symbol_info(symbol).trade_contract_size