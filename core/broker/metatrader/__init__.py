from core.size import Size
import pandas
import MetaTrader5
from dataclasses import dataclass, field
from typing import Iterable, TYPE_CHECKING

from core.chart import TickChart
from core.position import Position, PositionStatus, PositionType
from core.order import Order, OrderStatus, OrderType
from core.repository import MetaTraderRepository
from core.broker.broker import Broker
from core.broker.metatrader.serializers import MetaTraderSerializers

if TYPE_CHECKING:
	from core.chart import Symbol
from core.utils.time import TimestampLike
from core.utils.logging import logging
from core.utils.cls import pretty_repr

logger = logging.getLogger(__name__)

@dataclass
class MetaTraderBroker(Broker):
	id = 6969
	serializers = MetaTraderSerializers()
	repository: MetaTraderRepository = field(default_factory = MetaTraderRepository)

	def place_order(self, order: Order) -> Order:
		if isinstance(order.size, Size):
			order.size = order.size.to(Size.Lot, order = order)
		request = dict(
			action = MetaTrader5.TRADE_ACTION_DEAL,
			symbol = order.symbol,
			volume = float(order.size),
			type = MetaTrader5.ORDER_TYPE_BUY if order.type == 'buy' else MetaTrader5.ORDER_TYPE_SELL,
			magic = self.id,
			type_filling = MetaTrader5.ORDER_FILLING_IOC,
		)

		if order.limit:
			request['price'] = float(order.limit)
		if order.sl: 
			request['sl'] = float(order.sl)
		if order.tp: 
			request['tp'] = float(order.tp)
		
		response = MetaTrader5.order_send(request)
		if response == None or response.retcode != MetaTrader5.TRADE_RETCODE_DONE:
			logger.error(
				(
					f'Failed to place order.\n'
					f'Order: {pretty_repr(order)}\n'
					f'Request: {pretty_repr(request)}\n'
					f'Response: {response}\n'
					f'Last MetaTrader Error: {MetaTrader5.last_error()}\n'
				)
			)
		else:
			order.status = 'placed'
			order.id = response.order,
			order.open_timestamp = self.now

		return order

	def cancel_order(self, order: Order) -> Order:
		request = dict(
			action = MetaTrader5.TRADE_ACTION_REMOVE,
			order = order.id
		)
		response = MetaTrader5.order_send(request)

		if response == None or response.retcode != MetaTrader5.TRADE_RETCODE_DONE:
			logger.error(
				(
					f'Failed to cancel order.\n'
					f'Order: {pretty_repr(order)}\n'
					f'Request: {pretty_repr(request)}\n'
					f'Response: {response}\n'
					f'Last MetaTrader Error: {MetaTrader5.last_error()}\n'
				)
			)
		else:
			order.status = 'canceled'
			order.close_timestamp = self.now

		return order

	def close_position(self, position: Position):
		request = dict(
			action = MetaTrader5.TRADE_ACTION_DEAL,
			type = MetaTrader5.ORDER_TYPE_SELL if position.type == 'buy' else MetaTrader5.ORDER_TYPE_BUY,
			volume = float(position.size),
			position = position.id,
		)

		response = MetaTrader5.order_send(request)
		if response == None or response.retcode != MetaTrader5.TRADE_RETCODE_DONE:
			logger.error(
				(
					f'Failed to close position.\n'
					f'Position: {pretty_repr(position)}\n'
					f'Request: {pretty_repr(request)}\n'
					f'Response: {response}\n'
					f'Last MetaTrader Error: {MetaTrader5.last_error()}\n'
				)
			)
		else:
			position.exit_price = response.price
			position.status = 'closed'
			position.close_timestamp = self.now

		return position

	def get_orders(
		self,
		symbol: 'Symbol' = None,
		type: OrderType = None,
		from_timestamp: TimestampLike = pandas.Timestamp(0),
		to_timestamp: TimestampLike = None,
		status: OrderStatus = 'open',
	) -> Iterable[Order]:
		if from_timestamp == None:
			from_timestamp = pandas.Timestamp(0)
		if to_timestamp == None:
			to_timestamp = self.now

		if status == 'open':
			orders = MetaTrader5.orders_get(symbol = symbol)
		else:
			orders = MetaTrader5.history_orders_get(
				date_from = from_timestamp.to_pydatetime(),
				date_to = to_timestamp.to_pydatetime(),
				group = symbol,
			)
		if orders == None:
			logger.error(
				(
					f'Failed to get orders.\n'
					f'Last MetaTrader Error: {MetaTrader5.last_error()}\n'
				)
			)
		for order in orders:
			order = self.serializers.order.to_order(order)

			if status != None and order.status != status:
				continue

			if type != None and order.type != type:
				continue

			if order.open_timestamp < from_timestamp:
				continue

			if order.open_timestamp > to_timestamp:
				continue

			order.broker = self
			yield order

	def get_positions(
		self,
		symbol: 'Symbol' = None,
		type: PositionType = None,
		from_timestamp: TimestampLike = None,
		to_timestamp: TimestampLike = None,
		status: PositionStatus = 'open',
	) -> Iterable[Position]:
		if from_timestamp == None:
			from_timestamp = pandas.Timestamp(0)
		if to_timestamp == None:
			to_timestamp = self.now

		if status == 'open':
			positions = MetaTrader5.positions_get(symbol = symbol)
		else: 
			raise Exception('Getting `closed` positions is currently not supported by MetaTraderBroker')
		for position in positions:
			position = self.serializers.position.to_position(position)

			if status != None and position.status != status:
				continue

			if type != None and position.type != type:
				continue

			if position.open_timestamp < from_timestamp:
				continue

			if position.open_timestamp > to_timestamp:
				continue

			position.broker = self
			yield position


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

		symbol_info = MetaTrader5.symbol_info(symbol)
		return (symbol_info.ask + symbol_info.bid) / 2