import pandas
import MetaTrader5

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

	def to_order(self, order):
		return Order(
			id = order.ticket,
			type = self.type.serialize(order.type),
			symbol = order.symbol,
			size = order.volume_current,
			limit = None,
			stop = order.price_stoplimit,
			sl = order.sl,
			tp = order.tp,
			open_timestamp = pandas.Timestamp(order.time_setup_msc, unit='ms'),
			close_timestamp = pandas.Timestamp(order.time_done_msc, unit = 'ms'),
			status = self.status.serialize(order.status),
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
			size = position.volume,
			entry_price = position.price_open,
			open_timestamp = pandas.Timestamp(position.time_msc, unit = 'ms'),
			tp = position.tp,
			sl = position.sl,
			status = 'open'
		)

class MetaTraderSerializers:
	order = MetaTraderOrderSerializer()
	position = MetaTraderPositionSerializer()