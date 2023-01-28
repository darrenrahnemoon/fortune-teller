from argparse import ArgumentParser, Namespace
from apps.next_period_high_low.container import NextPeriodHighLowContainer
from core.broker import MetaTraderBroker
from core.utils.time import normalize_timestamp, now

def config(parser: ArgumentParser):
	parser.add_argument('--timestamp', default = now(), type = normalize_timestamp)
	parser.add_argument('--environment', default = 'validation')
def handler(args: Namespace):
	print('As of:', args.timestamp)
	container = NextPeriodHighLowContainer.get()
	strategy_config = container.config.get('strategy')
	if args.environment == 'production':
		strategy_config.metatrader_broker = MetaTraderBroker()

	strategy = container.strategy()
	prediction = strategy.get_prediction_for_largest_change(args.timestamp)
	print('chart:', prediction['chart'].name)
	print('price:', prediction['from_price'])
	print('high:', prediction['high'])
	print('low:', prediction['low'])
	print('action:', prediction['action'])