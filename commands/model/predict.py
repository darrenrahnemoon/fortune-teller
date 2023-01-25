from argparse import ArgumentParser, Namespace
from apps.next_period_high_low.container import NextPeriodHighLowContainer

from core.repository import MetaTraderRepository
from core.utils.time import normalize_timestamp, now

def config(parser: ArgumentParser):
	parser.add_argument('timestamp', default = now(), type = normalize_timestamp)

def handler(args: Namespace):
	container = NextPeriodHighLowContainer.get()
	container.config.metatrader_repository.from_value(MetaTraderRepository())
	tuner = container.tuner()
	tuner.predict_with_best_model(args.timestamp)