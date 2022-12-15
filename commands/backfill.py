from core.utils.cls import product_dict
import itertools
import logging
from numpy import e
import pandas

from core.interval import * # Needed for `eval`
from core.chart import CandleStickChart, TickChart, LineChart
from core.broker import SimulationBroker
from core.utils.command import Command, map_dict_to_argument
from core.utils.module import import_module
from core.utils.time import normalize_timestamp, now

logger = logging.getLogger(__name__)

class BackfillHistoricalDataCommand(Command):
	brokers = {
		'MetaTrader'  : lambda: import_module('core.broker.metatrader').MetaTraderBroker,
		'AlphaVantage': lambda: import_module('core.broker.alphavantage').AlphaVantageBroker,
	}
	charts = {
		'LineChart': LineChart,
		'CandleStickChart' : CandleStickChart,
		'TickChart' : TickChart,
	}
	def config(self):
		self.parser.add_argument('symbol', nargs='*', default=[])
		self.parser.add_argument('--chart', nargs="+", **map_dict_to_argument(self.charts), default=list(self.charts.values()))
		self.parser.add_argument('--broker', **map_dict_to_argument(self.brokers))
		self.parser.add_argument('--from', dest='from_timestamp', type=normalize_timestamp)
		self.parser.add_argument('--to', dest='to_timestamp', default=now(), type=normalize_timestamp)

		# Additional chart query fields that are being manually maintained for now until we find a better solution
		self.parser.add_argument('--interval', nargs='+', type=lambda interval: eval(interval), default=[])
		self.parser.add_argument('--maturity', nargs='+', type=lambda interval: eval(interval), default=[])

	def handler(self):
		if not self.args.broker:
			logger.error('You need to specify a broker to backfill from.')
			return

		from_broker: Broker = self.args.broker()()
		to_broker = SimulationBroker()
		combinations = {
			'chart': self.args.chart,
			'symbol': self.args.symbol,
			'interval': self.args.interval,
			'maturity': self.args.maturity,
		}
		combinations = { key: value for key, value in combinations.items() if len(value) }

		for combination in product_dict(combinations):
			increments = []
			chart_class = combination.pop('chart')
			chart = chart_class(**combination)
			if isinstance(chart, TickChart):
				increments = pandas.date_range(
					start=self.args.from_timestamp,
					end=self.args.to_timestamp,
					freq='MS' # "Month Start"
				)
			if len(increments) == 0:
				increments = [ self.args.from_timestamp, self.args.to_timestamp ]

			for index in range(1, len(increments)):
				chart.from_timestamp = increments[index - 1]
				chart.to_timestamp = increments[index]
				logger.info(f'Backfilling {chart}...')
				from_broker.read_chart(chart)
				to_broker.write_chart(chart)
