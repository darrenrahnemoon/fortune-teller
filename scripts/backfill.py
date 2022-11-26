import itertools
import logging
from numpy import e
import pandas

from core.interval import Interval # Needed for `eval`
from core.chart import CandleStickChart, TickChart, LineChart
from core.broker import SimulationBroker
from core.utils.command import Command, map_dict_to_argument
from core.utils.module import import_module
from core.utils.collection import ensure_list
from core.utils.time import normalize_timestamp, now

logger = logging.getLogger(__name__)

class BackfillHistoricalDataCommand(Command):
	brokers = {
		'MetaTrader'  : lambda: import_module('core.broker.metatrader').MetaTraderBroker,
		'AlphaVantage': lambda: import_module('core.broker.alphavantage').AlphaVantageBroker,
	}
	charts = {
		'Line': LineChart,
		'CandleStick' : CandleStickChart,
		'Tick' : TickChart,
	}
	def config(self):
		self.parser.add_argument('symbol', nargs='*')
		self.parser.add_argument('--chart', nargs="+", **map_dict_to_argument(self.charts))
		self.parser.add_argument('--broker', **map_dict_to_argument(self.brokers))
		self.parser.add_argument('--from', dest='from_timestamp', type=normalize_timestamp)
		self.parser.add_argument('--to', dest='to_timestamp', default=now(), type=normalize_timestamp)

		# Additional chart query fields that are being manually maintained for now until we find a better solution
		self.parser.add_argument('--interval', nargs='+', type=lambda interval: eval(f'Interval.{interval}'))
		self.parser.add_argument('--maturity', nargs='+', type=lambda interval: eval(f'Interval.{interval}'))

	def handler(self):
		if not self.args.broker:
			logger.error('You need to specify a broker to backfill from.')
			return
		# called twice: once for lambda to import, once for construction of broker instance 
		from_broker = self.args.broker()()
		available_data = from_broker.available_data

		to_broker = SimulationBroker()
		if not self.args.symbol:
			logger.info(f"Getting all available symbols:\n{', '.join(list(available_data.keys()))}\n")

		for symbol in ensure_list(self.args.symbol) or available_data.keys():
			if symbol not in available_data:
				logger.warn(f"Symbol '{symbol}' was not found in broker's available data. Skipping...")
				continue

			available_charts_and_combinations = available_data[symbol]
			for chart_class in ensure_list(self.args.chart) or list(available_charts_and_combinations.keys()):
				if chart_class not in available_charts_and_combinations:
					logging.warn(f"Broker does not support '{chart_class.__name__}' type for symbol '{symbol}'. Skipping...")
					continue

				combinations: dict[str, list] = available_charts_and_combinations[chart_class]

				# Reduce the combination of field values based on passed options from cli
				for key in [ 'interval', 'maturity' ]:
					override_value = getattr(self.args, key)
					if override_value and key in combinations:
						combinations[key] = override_value

				if chart_class == TickChart:
					increments = pandas.date_range(
						start=self.args.from_timestamp,
						end=self.args.to_timestamp,
						freq='MS' # "Month Start"
					)
				else:
					increments = [ self.args.from_timestamp, self.args.to_timestamp ]

				for index in range(1, len(increments)):
					for combination in itertools.product(*combinations.values()):
						combination = dict(zip(combinations.keys(), combination))
						chart = chart_class(
							broker=from_broker,
							symbol=symbol,
							from_timestamp=increments[index - 1],
							to_timestamp=increments[index],
							**combination
						)
						logger.info(f'Backfilling {chart}...')
						chart.read(from_broker).write(to_broker)