import pandas
import MetaTrader5

from core.size import Size
from core.order import Order
from core.position import Position
from core.utils.serializer import Serializer, MappingSerializer

class MetaTraderOrderSerializer(Serializer):
	status = MappingSerializer({
		MetaTrader5.ORDER_STATE_STARTED : 'open',
		MetaTrader5.ORDER_STATE_PLACED : 'open',
		MetaTrader5.ORDER_STATE_PARTIAL : 'filled',
		MetaTrader5.ORDER_STATE_FILLED : 'filled',
		MetaTrader5.ORDER_STATE_CANCELED : 'cancelled',
		MetaTrader5.ORDER_STATE_REJECTED : 'cancelled',
		MetaTrader5.ORDER_STATE_EXPIRED : 'cancelled',
	})

	type = MappingSerializer({
		MetaTrader5.ORDER_TYPE_BUY : 'buy',
		MetaTrader5.ORDER_TYPE_BUY_LIMIT : 'buy',
		MetaTrader5.ORDER_TYPE_BUY_STOP : 'buy',
		MetaTrader5.ORDER_TYPE_BUY_STOP_LIMIT : 'buy',
		MetaTrader5.ORDER_TYPE_SELL : 'sell',
		MetaTrader5.ORDER_TYPE_SELL_LIMIT : 'sell',
		MetaTrader5.ORDER_TYPE_SELL_STOP : 'sell',
		MetaTrader5.ORDER_TYPE_SELL_STOP_LIMIT : 'sell',
	})

	def to_metatrader_size(self, size: Size):
		return round(size.to(Size.Lot), 2)

	def to_metatrader_action(self, order: Order):
		if order.limit or order.stop:
			return MetaTrader5.TRADE_ACTION_PENDING
		return MetaTrader5.TRADE_ACTION_DEAL

	def to_metatrader_type(self, order: Order):
		if order.type == 'buy':
			if order.stop and order.limit:
				return MetaTrader5.ORDER_TYPE_BUY_STOP_LIMIT
			elif order.limit:
				return MetaTrader5.ORDER_TYPE_BUY_LIMIT
			elif order.stop:
				return MetaTrader5.ORDER_TYPE_BUY_STOP
			return MetaTrader5.ORDER_TYPE_BUY
		elif order.type == 'sell':
			if order.stop and order.limit:
				return MetaTrader5.ORDER_TYPE_SELL_STOP_LIMIT
			elif order.limit:
				return MetaTrader5.ORDER_TYPE_SELL_LIMIT
			elif order.stop:
				return MetaTrader5.ORDER_TYPE_SELL_STOP
			return MetaTrader5.ORDER_TYPE_SELL
		else:
			raise Exception(f'{order} missing `type`.')

	def to_order(self, order):
		return Order(
			id = order.ticket,
			type = self.type.serialize(order.type),
			symbol = order.symbol,
			size = Size.Lot(order.volume_current),
			limit = None if order.price_open == 0 else order.price_open,
			stop = None if order.price_stoplimit == 0 else order.price_stoplimit,
			sl = None if order.sl == 0 else order.sl,
			tp = None if order.tp == 0 else order.tp,
			open_timestamp = None if order.time_setup_msc == 0 else pandas.Timestamp(order.time_setup_msc, unit='ms', tz = 'UTC'),
			close_timestamp = None if order.time_done_msc == 0 else pandas.Timestamp(order.time_done_msc, unit = 'ms', tz = 'UTC'),
			status = self.status.serialize(order.state),
			position = order.position_id
		)

class MetaTraderPositionSerializer(Serializer):
	type = MappingSerializer({
		MetaTrader5.POSITION_TYPE_BUY : 'buy',
		MetaTrader5.POSITION_TYPE_SELL : 'sell',
	})

	def to_position(self, position):
		return Position(
			id = position.ticket,
			symbol = position.symbol,
			type = self.type.serialize(position.type),
			size = Size.Lot(position.volume),
			entry_price = position.price_open,
			open_timestamp = pandas.Timestamp(position.time_msc, unit = 'ms', tz = 'UTC'),
			tp = None if position.tp == 0 else position.tp,
			sl = None if position.sl == 0 else position.sl,
			status = 'open',
			order = position.identifier
		)

class MetaTraderSerializers:
	order = MetaTraderOrderSerializer()
	position = MetaTraderPositionSerializer()