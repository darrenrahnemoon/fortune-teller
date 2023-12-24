import pandas
from dataclasses import dataclass, field
from apps.pelosi_predictor.container import PelosiPredictorContainer
from apps.pelosi_predictor.config import PelosiPredictorConfig
from core.broker.simulation import SimulationBroker
from core.utils.time import normalize_timestamp, now

from core.utils.command import CommandSession
from core.utils.container.command import ContainerCommandSession

@dataclass
class BacktestStrategyCommandSession(
	ContainerCommandSession,
	CommandSession
):
	config: PelosiPredictorConfig = field(default_factory = PelosiPredictorConfig)
	container: PelosiPredictorContainer = None

	def setup(self):
		super().setup()
		self.parser.add_argument('--from', dest = 'from_timestamp', default = now() - pandas.Timedelta(365, 'day'), type = normalize_timestamp)
		self.parser.add_argument('--to', dest = 'to_timestamp', default = now(), type = normalize_timestamp)

	def run(self):
		super().run()
		strategy = self.container.strategy()
		broker: SimulationBroker = self.config.strategy.metatrader_broker
		broker.timesteps = pandas.date_range(
			self.args.from_timestamp,
			self.args.to_timestamp,
			freq = self.config.strategy.interval.to_pandas_frequency()
		)
		broker.backtest(strategy)