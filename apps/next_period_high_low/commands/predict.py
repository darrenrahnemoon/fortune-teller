from argparse import ArgumentParser, Namespace

from apps.next_period_high_low.container import NextPeriodHighLowContainer
from apps.next_period_high_low.config import NextPeriodHighLowConfig

from core.utils.time import normalize_timestamp, now
import core.utils.command.config

def config(parser: ArgumentParser):
	core.utils.command.config.add_fields_to_arguments(parser, NextPeriodHighLowConfig)
	parser.add_argument('--timestamp', default = now(), type = normalize_timestamp)

def handler(args: Namespace):
	print('As of:', args.timestamp)

	config = core.utils.command.config.set_fields_from_arguments(args, NextPeriodHighLowConfig())
	container = NextPeriodHighLowContainer(config = config)
	strategy = container.strategy()
	prediction = strategy.get_prediction_with_largest_change(args.timestamp)
	print('symbol:', prediction.symbol)
	print('price:', prediction.last_price)
	print('high:', prediction.high)
	print('low:', prediction.low)
	print('action:', prediction.action)