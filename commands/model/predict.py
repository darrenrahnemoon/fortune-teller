from argparse import ArgumentParser, Namespace
from apps.next_period_high_low.container import NextPeriodHighLowContainer
from core.repository import MetaTraderRepository
from core.utils.time import normalize_timestamp, now

def config(parser: ArgumentParser):
	parser.add_argument('timestamp', default = now(), type = normalize_timestamp)

def handler(args: Namespace):
	container = NextPeriodHighLowContainer.get()
	# container.config.metatrader_repository.from_value(MetaTraderRepository())
	strategy_config = container.config.get('strategy')
	tuner = container.tuner()
	predictions = tuner.predict_with_best_model(args.timestamp)
	max_high = max(predictions, key = lambda prediction: prediction[1]['high'])
	min_low = min(predictions, key = lambda prediction: prediction[1]['low'])
	for chart, prediction in predictions:
		chart.read(
			from_timestamp = args.timestamp,
			count = strategy_config.forward_window_length
		)
		if (chart.name == max_high[0].name):
			print('Max High')
		if (chart.name == min_low[0].name):
			print('Min Low')
		print(chart.name)
		print('high:', 'actual:', chart.data['high'].max(), 'predicted:', chart.data['high'].iloc[0] * (1 + prediction['high']), f"{prediction['high'] * 100}%")
		print('low: ', 'actual:', chart.data['low'].min(), 'predicted:', chart.data['low'].iloc[0] * (1 + prediction['low']), f"{prediction['low'] * 100}%")
		print('-------')
