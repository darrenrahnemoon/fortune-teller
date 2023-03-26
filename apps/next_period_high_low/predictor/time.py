from .base import NextPeriodHighLowPredictorService
from apps.next_period_high_low.preprocessor.time import NextPeriodHighLowTimePreprocessorService

class NextPeriodHighLowTimePredictorService(NextPeriodHighLowPredictorService):
	preprocessor_service: NextPeriodHighLowTimePreprocessorService = None
