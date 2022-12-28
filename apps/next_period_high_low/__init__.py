from .strategy import NextPeriodHighLowStrategy
from core.broker.simulation import SimulationBroker
from core.interval import Interval

def tune_model():
	broker = SimulationBroker()
	strategy = NextPeriodHighLowStrategy(
		alphavantage_broker=broker,
		metatrader_broker=broker,
		interval=Interval.Minute(1),
		backward_window_length=Interval.Minute(5),
		forward_window_length=Interval.Minute(2),
	)
	strategy.service.tune_model()