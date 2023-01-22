from apps.next_period_high_low.container import NextPeriodHighLowContainer

from core.repository import MetaTraderRepository
from core.utils.time import normalize_timestamp, now

def handler(args):
	container = NextPeriodHighLowContainer.get()
	container.config.metatrader_repository.from_value(MetaTraderRepository())
	service = container.service()
	print(service.predict(normalize_timestamp('2017-08-25')))