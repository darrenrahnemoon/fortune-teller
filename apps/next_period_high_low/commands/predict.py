from argparse import ArgumentParser, Namespace

from apps.next_period_high_low.container import NextPeriodHighLowContainer
from apps.next_period_high_low.config import NextPeriodHighLowConfig

from core.utils.time import normalize_timestamp, now
import core.utils.command.config

def config(parser: ArgumentParser):
	core.utils.command.config.add_args(parser, NextPeriodHighLowConfig)

	parser.add_argument('--timestamp', default = now(), type = normalize_timestamp)

def handler(args: Namespace):
	config = core.utils.command.config.create_config_from_args(args, NextPeriodHighLowConfig)

	print('As of:', args.timestamp)
	container = NextPeriodHighLowContainer.get(config = config)

	strategy = container.strategy()
	prediction = strategy.get_prediction_for_largest_change(args.timestamp)
	print('chart:', prediction['chart'].name)
	print('price:', prediction['last_price'])
	print('high:', prediction['high'])
	print('low:', prediction['low'])
	print('action:', prediction['action'])