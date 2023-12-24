from argparse import ArgumentParser, Namespace

from dataclasses import dataclass, field
from apps.pelosi_predictor.container import PelosiPredictorContainer
from apps.pelosi_predictor.config import PelosiPredictorConfig

from core.utils.command import CommandSession
from core.utils.container.command import ContainerCommandSession

@dataclass
class RunStrategyCommandSession(
	ContainerCommandSession,
	CommandSession
):
	config: PelosiPredictorConfig = None
	container: PelosiPredictorContainer = None

	def run(self):
		super().run()
		self.config.dataset.batch_size = 1
		strategy = self.container.strategy()
		strategy.run()
