from argparse import Namespace
from apps.next_period_high_low.container import NextPeriodHighLowContainer

def handler(args: Namespace):
	container = NextPeriodHighLowContainer.get()
	tuner_service = container.tuner_service()
	model = tuner_service.get_model('best')
	model.summary()