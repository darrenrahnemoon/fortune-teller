from argparse import Namespace
from apps.next_period_high_low.container import NextPeriodHighLowContainer

def handler(args: Namespace):
	container = NextPeriodHighLowContainer.get()
	tuner = container.tuner()
	model = tuner.get_best_model()
	model.summary()