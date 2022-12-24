from .strategy import NextPeriodHighLowStrategy
from core.broker.simulation import SimulationBroker
from core.interval import Interval

broker = SimulationBroker()
strategy = NextPeriodHighLowStrategy(
	alphavantage_broker=broker,
	metatrader_broker=broker,
	interval=Interval.Minute(1),
	backward_window_length=Interval.Minute(2),
	forward_window_length=Interval.Minute(2),
)

strategy.model_service.train()