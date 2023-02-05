import numpy
import pandas
from dataclasses import dataclass

from .serializers import MetaTraderSerializers
from core.repository.repository import Repository
from core.chart import CandleStickChart, TickChart, Chart, OverriddenChart
from core.utils.module import import_module
from core.utils.logging import logging

logger = logging.getLogger(__name__)

@dataclass
class MetaTraderRepository(Repository):
	timezone = 'UTC'
	serializers = MetaTraderSerializers()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		# Intentionally imported this way so that importing this package on MacOS and Linux doesn't bork about MetaTrader5 which is only available on Windows
		self.api = import_module('MetaTrader5')
		if not self.api.initialize():
			raise self.api.last_error()

	def get_available_symbols(self):
		return [ symbol.name for symbol in self.api.symbols_get() ]

	def get_available_chart_combinations(self):
		symbols = self.get_available_symbols()
		return {
			CandleStickChart : [
				{
					'symbol': [ symbol ],
					'interval' : list(self.serializers.interval.mapping.keys())
				}
				for symbol in symbols
			],
			TickChart : [
				{ 'symbol' : [ symbol ] }
				for symbol in symbols
			]
		}

	def read_chart(
		self,
		chart: Chart or OverriddenChart = None,
		**overrides
	) -> pandas.DataFrame:
		chart = OverriddenChart(chart, overrides)
		dataframe = None
		if chart.type == CandleStickChart:
			dataframe = self.read_raw_candlestick_chart(chart)
			dataframe = self.ensure_interval_integrity(
				dataframe = dataframe,
				chart = chart
			)
		elif chart.type == TickChart:
			dataframe = self.read_raw_tick_chart(chart)

		return dataframe

	def read_raw_tick_chart(self, chart: TickChart):
		if chart.count:
			records = self.api.copy_ticks_from(
				chart.symbol,
				chart.to_timestamp.to_pydatetime(),
				chart.count,
				self.api.COPY_TICKS_ALL,
			)
		else:
			records = self.api.copy_ticks_range(
				chart.symbol,
				chart.from_timestamp.to_pydatetime(),
				chart.to_timestamp.to_pydatetime(),
				self.api.COPY_TICKS_ALL
			)
		return self.serializers.records.tick.to_dataframe(
			records,
			name = chart.name,
			select = chart.select,
			tz = self.timezone,
		)

	def read_raw_candlestick_chart(self, chart: CandleStickChart):
		if chart.count:
			records = self.api.copy_rates_from(
				chart.symbol,
				self.serializers.interval.serialize(chart.interval),
				chart.to_timestamp.to_pydatetime(),
				chart.count
			)
		else:
			records = self.api.copy_rates_range(
				chart.symbol,
				self.serializers.interval.serialize(chart.interval),
				chart.from_timestamp.to_pydatetime(),
				chart.to_timestamp.to_pydatetime(),
			)
		return self.serializers.records.candlestick.to_dataframe(
			records,
			name = chart.name,
			select = chart.select,
			tz = self.timezone,
		)

	def ensure_interval_integrity(
		self,
		dataframe: pandas.DataFrame = None,
		chart: OverriddenChart = None,
		frequency_tolerance: int = 50,
	):
		if not (chart.from_timestamp and chart.to_timestamp and chart.interval):
			return dataframe # Not enough data to do an interval integrity 

		if len(dataframe) == 0:
			return dataframe

		try:
			average_frequency = numpy.diff(dataframe.index.to_numpy()).mean()
			expected_frequency = chart.interval.to_pandas_timedelta()
			if average_frequency / expected_frequency > frequency_tolerance:
				logger.warn(f"Missing too many data points. It's likely that MetaTrader attempted to compensate for less granularity by returning a higher granular data. Skipping results...\nAverage Frequency of Received Data: {average_frequency}\nExpected Frequency: {expected_frequency}")
				return self.serializers.records.candlestick.to_dataframe(
					[],
					name = chart.name,
					select = chart.select,
					tz = self.timezone,
				)
		except:
			pass
		return dataframe

# tick copy flags
COPY_TICKS_ALL                      = -1
COPY_TICKS_INFO                     = 1
COPY_TICKS_TRADE                    = 2
# tick flags						  
TICK_FLAG_BID                       = 0x02
TICK_FLAG_ASK                       = 0x04
TICK_FLAG_LAST                      = 0x08
TICK_FLAG_VOLUME                    = 0x10
TICK_FLAG_BUY                       = 0x20
TICK_FLAG_SELL                      = 0x40
# position type, ENUM_POSITION_TYPE
POSITION_TYPE_BUY                   = 0      # Buy
POSITION_TYPE_SELL                  = 1      # Sell
# position reason, ENUM_POSITION_REASON
POSITION_REASON_CLIENT              = 0      # The position was opened as a result of activation of an order placed from a desktop terminal
POSITION_REASON_MOBILE              = 1      # The position was opened as a result of activation of an order placed from a mobile application
POSITION_REASON_WEB                 = 2      # The position was opened as a result of activation of an order placed from the web platform
POSITION_REASON_EXPERT              = 3      # The position was opened as a result of activation of an order placed from an MQL5 program, i.e. an Expert Advisor or a script
# order types, ENUM_ORDER_TYPE
ORDER_TYPE_BUY                      = 0      # Market Buy order
ORDER_TYPE_SELL                     = 1      # Market Sell order
ORDER_TYPE_BUY_LIMIT                = 2      # Buy Limit pending order
ORDER_TYPE_SELL_LIMIT               = 3      # Sell Limit pending order
ORDER_TYPE_BUY_STOP                 = 4      # Buy Stop pending order
ORDER_TYPE_SELL_STOP                = 5      # Sell Stop pending order
ORDER_TYPE_BUY_STOP_LIMIT           = 6      # Upon reaching the order price, a pending Buy Limit order is placed at the StopLimit price
ORDER_TYPE_SELL_STOP_LIMIT          = 7      # Upon reaching the order price, a pending Sell Limit order is placed at the StopLimit price
ORDER_TYPE_CLOSE_BY                 = 8      # Order to close a position by an opposite one
# order state, ENUM_ORDER_STATE
ORDER_STATE_STARTED                 = 0      # Order checked, but not yet accepted by broker
ORDER_STATE_PLACED                  = 1      # Order accepted
ORDER_STATE_CANCELED                = 2      # Order canceled by client
ORDER_STATE_PARTIAL                 = 3      # Order partially executed
ORDER_STATE_FILLED                  = 4      # Order fully executed
ORDER_STATE_REJECTED                = 5      # Order rejected
ORDER_STATE_EXPIRED                 = 6      # Order expired
ORDER_STATE_REQUEST_ADD             = 7      # Order is being registered (placing to the trading system)
ORDER_STATE_REQUEST_MODIFY          = 8      # Order is being modified (changing its parameters)
ORDER_STATE_REQUEST_CANCEL          = 9      # Order is being deleted (deleting from the trading system)
# ENUM_ORDER_TYPE_FILLING
ORDER_FILLING_FOK                   = 0
ORDER_FILLING_IOC                   = 1
ORDER_FILLING_RETURN                = 2
# ENUM_ORDER_TYPE_TIME
ORDER_TIME_GTC                      = 0      # Good till cancel order
ORDER_TIME_DAY                      = 1      # Good till current trade day order
ORDER_TIME_SPECIFIED                = 2      # Good till expired order
ORDER_TIME_SPECIFIED_DAY            = 3      # The order will be effective till 23:59:59 of the specified day. If this time is outside a trading session, the order expires in the nearest trading time.
# ENUM_ORDER_REASON
ORDER_REASON_CLIENT                 = 0      # The order was placed from a desktop terminal
ORDER_REASON_MOBILE                 = 1      # The order was placed from a mobile application
ORDER_REASON_WEB                    = 2      # The order was placed from a web platform
ORDER_REASON_EXPERT                 = 3      # The order was placed from an MQL5-program, i.e. by an Expert Advisor or a script
ORDER_REASON_SL                     = 4      # The order was placed as a result of Stop Loss activation
ORDER_REASON_TP                     = 5      # The order was placed as a result of Take Profit activation
ORDER_REASON_SO                     = 6      # The order was placed as a result of the Stop Out event
# deal types, ENUM_DEAL_TYPE
DEAL_TYPE_BUY                       = 0      # Buy
DEAL_TYPE_SELL                      = 1      # Sell
DEAL_TYPE_BALANCE                   = 2      # Balance
DEAL_TYPE_CREDIT                    = 3      # Credit
DEAL_TYPE_CHARGE                    = 4      # Additional charge
DEAL_TYPE_CORRECTION                = 5      # Correction
DEAL_TYPE_BONUS                     = 6      # Bonus
DEAL_TYPE_COMMISSION                = 7      # Additional commission
DEAL_TYPE_COMMISSION_DAILY          = 8      # Daily commission
DEAL_TYPE_COMMISSION_MONTHLY        = 9      # Monthly commission
DEAL_TYPE_COMMISSION_AGENT_DAILY    = 10     # Daily agent commission
DEAL_TYPE_COMMISSION_AGENT_MONTHLY  = 11     # Monthly agent commission
DEAL_TYPE_INTEREST                  = 12     # Interest rate
DEAL_TYPE_BUY_CANCELED              = 13     # Canceled buy deal.
DEAL_TYPE_SELL_CANCELED             = 14     # Canceled sell deal.
DEAL_DIVIDEND                       = 15     # Dividend operations
DEAL_DIVIDEND_FRANKED               = 16     # Franked (non-taxable) dividend operations
DEAL_TAX                            = 17     # Tax charges
# ENUM_DEAL_ENTRY
DEAL_ENTRY_IN                       = 0      # Entry in
DEAL_ENTRY_OUT                      = 1      # Entry out
DEAL_ENTRY_INOUT                    = 2      # Reverse
DEAL_ENTRY_OUT_BY                   = 3      # Close a position by an opposite one
# ENUM_DEAL_REASON
DEAL_REASON_CLIENT                  = 0      # The deal was executed as a result of activation of an order placed from a desktop terminal
DEAL_REASON_MOBILE                  = 1      # The deal was executed as a result of activation of an order placed from a mobile application
DEAL_REASON_WEB                     = 2      # The deal was executed as a result of activation of an order placed from the web platform
DEAL_REASON_EXPERT                  = 3      # The deal was executed as a result of activation of an order placed from an MQL5 program, i.e. an Expert Advisor or a script
DEAL_REASON_SL                      = 4      # The deal was executed as a result of Stop Loss activation
DEAL_REASON_TP                      = 5      # The deal was executed as a result of Take Profit activation
DEAL_REASON_SO                      = 6      # The deal was executed as a result of the Stop Out event
DEAL_REASON_ROLLOVER                = 7      # The deal was executed due to a rollover
DEAL_REASON_VMARGIN                 = 8      # The deal was executed after charging the variation margin
DEAL_REASON_SPLIT                   = 9      # The deal was executed after the split (price reduction) of an instrument, which had an open position during split announcement
# ENUM_TRADE_REQUEST_ACTIONS, Trade Operation Types
TRADE_ACTION_DEAL                   = 1      # Place a trade order for an immediate execution with the specified parameters (market order)
TRADE_ACTION_PENDING                = 5      # Place a trade order for the execution under specified conditions (pending order)
TRADE_ACTION_SLTP                   = 6      # Modify Stop Loss and Take Profit values of an opened position
TRADE_ACTION_MODIFY                 = 7      # Modify the parameters of the order placed previously
TRADE_ACTION_REMOVE                 = 8      # Delete the pending order placed previously
TRADE_ACTION_CLOSE_BY               = 10     # Close a position by an opposite one
# ENUM_SYMBOL_CHART_MODE
SYMBOL_CHART_MODE_BID               = 0
SYMBOL_CHART_MODE_LAST              = 1
# ENUM_SYMBOL_CALC_MODE
SYMBOL_CALC_MODE_FOREX              = 0
SYMBOL_CALC_MODE_FUTURES            = 1
SYMBOL_CALC_MODE_CFD                = 2
SYMBOL_CALC_MODE_CFDINDEX           = 3
SYMBOL_CALC_MODE_CFDLEVERAGE        = 4
SYMBOL_CALC_MODE_FOREX_NO_LEVERAGE  = 5
SYMBOL_CALC_MODE_EXCH_STOCKS        = 32
SYMBOL_CALC_MODE_EXCH_FUTURES       = 33
SYMBOL_CALC_MODE_EXCH_OPTIONS       = 34
SYMBOL_CALC_MODE_EXCH_OPTIONS_MARGIN= 36
SYMBOL_CALC_MODE_EXCH_BONDS         = 37
SYMBOL_CALC_MODE_EXCH_STOCKS_MOEX   = 38
SYMBOL_CALC_MODE_EXCH_BONDS_MOEX    = 39
SYMBOL_CALC_MODE_SERV_COLLATERAL    = 64
# ENUM_SYMBOL_TRADE_MODE
SYMBOL_TRADE_MODE_DISABLED          = 0
SYMBOL_TRADE_MODE_LONGONLY          = 1
SYMBOL_TRADE_MODE_SHORTONLY         = 2
SYMBOL_TRADE_MODE_CLOSEONLY         = 3
SYMBOL_TRADE_MODE_FULL              = 4
# ENUM_SYMBOL_TRADE_EXECUTION
SYMBOL_TRADE_EXECUTION_REQUEST      = 0
SYMBOL_TRADE_EXECUTION_INSTANT      = 1
SYMBOL_TRADE_EXECUTION_MARKET       = 2
SYMBOL_TRADE_EXECUTION_EXCHANGE     = 3
# ENUM_SYMBOL_SWAP_MODE
SYMBOL_SWAP_MODE_DISABLED           = 0
SYMBOL_SWAP_MODE_POINTS             = 1
SYMBOL_SWAP_MODE_CURRENCY_SYMBOL    = 2
SYMBOL_SWAP_MODE_CURRENCY_MARGIN    = 3
SYMBOL_SWAP_MODE_CURRENCY_DEPOSIT   = 4
SYMBOL_SWAP_MODE_INTEREST_CURRENT   = 5
SYMBOL_SWAP_MODE_INTEREST_OPEN      = 6
SYMBOL_SWAP_MODE_REOPEN_CURRENT     = 7
SYMBOL_SWAP_MODE_REOPEN_BID         = 8
# ENUM_DAY_OF_WEEK
DAY_OF_WEEK_SUNDAY                  = 0
DAY_OF_WEEK_MONDAY                  = 1
DAY_OF_WEEK_TUESDAY                 = 2
DAY_OF_WEEK_WEDNESDAY               = 3
DAY_OF_WEEK_THURSDAY                = 4
DAY_OF_WEEK_FRIDAY                  = 5
DAY_OF_WEEK_SATURDAY                = 6
# ENUM_SYMBOL_ORDER_GTC_MODE
SYMBOL_ORDERS_GTC                   = 0
SYMBOL_ORDERS_DAILY                 = 1
SYMBOL_ORDERS_DAILY_NO_STOPS        = 2
# ENUM_SYMBOL_OPTION_RIGHT
SYMBOL_OPTION_RIGHT_CALL            = 0
SYMBOL_OPTION_RIGHT_PUT             = 1
# ENUM_SYMBOL_OPTION_MODE
SYMBOL_OPTION_MODE_EUROPEAN         = 0
SYMBOL_OPTION_MODE_AMERICAN         = 1
# ENUM_ACCOUNT_TRADE_MODE
ACCOUNT_TRADE_MODE_DEMO             = 0
ACCOUNT_TRADE_MODE_CONTEST          = 1
ACCOUNT_TRADE_MODE_REAL             = 2
# ENUM_ACCOUNT_STOPOUT_MODE
ACCOUNT_STOPOUT_MODE_PERCENT        = 0
ACCOUNT_STOPOUT_MODE_MONEY          = 1
# ENUM_ACCOUNT_MARGIN_MODE
ACCOUNT_MARGIN_MODE_RETAIL_NETTING  = 0
ACCOUNT_MARGIN_MODE_EXCHANGE        = 1
ACCOUNT_MARGIN_MODE_RETAIL_HEDGING  = 2
# ENUM_BOOK_TYPE
BOOK_TYPE_SELL                      = 1
BOOK_TYPE_BUY                       = 2
BOOK_TYPE_SELL_MARKET               = 3
BOOK_TYPE_BUY_MARKET                = 4
# order send/check return codes
TRADE_RETCODE_REQUOTE               = 10004
TRADE_RETCODE_REJECT                = 10006
TRADE_RETCODE_CANCEL                = 10007
TRADE_RETCODE_PLACED                = 10008
TRADE_RETCODE_DONE                  = 10009
TRADE_RETCODE_DONE_PARTIAL          = 10010
TRADE_RETCODE_ERROR                 = 10011
TRADE_RETCODE_TIMEOUT               = 10012
TRADE_RETCODE_INVALID               = 10013
TRADE_RETCODE_INVALID_VOLUME        = 10014
TRADE_RETCODE_INVALID_PRICE         = 10015
TRADE_RETCODE_INVALID_STOPS         = 10016
TRADE_RETCODE_TRADE_DISABLED        = 10017
TRADE_RETCODE_MARKET_CLOSED         = 10018
TRADE_RETCODE_NO_MONEY              = 10019
TRADE_RETCODE_PRICE_CHANGED         = 10020
TRADE_RETCODE_PRICE_OFF             = 10021
TRADE_RETCODE_INVALID_EXPIRATION    = 10022
TRADE_RETCODE_ORDER_CHANGED         = 10023
TRADE_RETCODE_TOO_MANY_REQUESTS     = 10024
TRADE_RETCODE_NO_CHANGES            = 10025
TRADE_RETCODE_SERVER_DISABLES_AT    = 10026
TRADE_RETCODE_CLIENT_DISABLES_AT    = 10027
TRADE_RETCODE_LOCKED                = 10028
TRADE_RETCODE_FROZEN                = 10029
TRADE_RETCODE_INVALID_FILL          = 10030
TRADE_RETCODE_CONNECTION            = 10031
TRADE_RETCODE_ONLY_REAL             = 10032
TRADE_RETCODE_LIMIT_ORDERS          = 10033
TRADE_RETCODE_LIMIT_VOLUME          = 10034
TRADE_RETCODE_INVALID_ORDER         = 10035
TRADE_RETCODE_POSITION_CLOSED       = 10036
TRADE_RETCODE_INVALID_CLOSE_VOLUME  = 10038
TRADE_RETCODE_CLOSE_ORDER_EXIST     = 10039
TRADE_RETCODE_LIMIT_POSITIONS       = 10040
TRADE_RETCODE_REJECT_CANCEL         = 10041
TRADE_RETCODE_LONG_ONLY             = 10042
TRADE_RETCODE_SHORT_ONLY            = 10043
TRADE_RETCODE_CLOSE_ONLY            = 10044
TRADE_RETCODE_FIFO_CLOSE            = 10045
# functio error codes, last_error()
RES_S_OK                            =1           # generic success
RES_E_FAIL                          =-1          # generic fail
RES_E_INVALID_PARAMS                =-2          # invalid arguments/parameters
RES_E_NO_MEMORY                     =-3          # no memory condition
RES_E_NOT_FOUND                     =-4          # no history
RES_E_INVALID_VERSION               =-5          # invalid version
RES_E_AUTH_FAILED                   =-6          # authorization failed
RES_E_UNSUPPORTED                   =-7          # unsupported method
RES_E_AUTO_TRADING_DISABLED         =-8          # auto-trading disabled
RES_E_INTERNAL_FAIL                 =-10000      # internal IPC general error
RES_E_INTERNAL_FAIL_SEND            =-10001      # internal IPC send failed
RES_E_INTERNAL_FAIL_RECEIVE         =-10002      # internal IPC recv failed
RES_E_INTERNAL_FAIL_INIT            =-10003      # internal IPC initialization fail
RES_E_INTERNAL_FAIL_CONNECT         =-10004      # internal IPC no ipc
RES_E_INTERNAL_FAIL_TIMEOUT         =-10005      # internal timeout
