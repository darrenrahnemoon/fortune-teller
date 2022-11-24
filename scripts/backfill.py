import itertools
import logging

from lib.interval import Interval # Needed for `eval`
from lib.chart import CandleStickChart, TickChart, LineChart
from lib.broker import SimulationBroker
from lib.utils.command import Command, map_dict_to_argument
from lib.utils.module import import_module
from lib.utils.collection import ensure_list

logger = logging.getLogger(__name__)

class BackfillHistoricalDataCommand(Command):
	brokers = {
		'MetaTrader'  : lambda: import_module('lib.broker.metatrader').MetaTraderBroker,
		'AlphaVantage': lambda: import_module('lib.broker.alphavantage').AlphaVantageBroker,
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
		self.parser.add_argument('--from', dest='from_timestamp')
		self.parser.add_argument('--to', dest='to_timestamp')

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

				for combination in itertools.product(*combinations.values()):
					combination = dict(zip(combinations.keys(), combination))
					chart = chart_class(
						broker=from_broker,
						symbol=symbol,
						from_timestamp=self.args.from_timestamp,
						to_timestamp=self.args.to_timestamp,
						**combination
					)\
					.read(from_broker)\
					.write(to_broker)