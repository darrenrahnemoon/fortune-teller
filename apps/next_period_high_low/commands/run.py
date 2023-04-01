from argparse import ArgumentParser, Namespace

from dataclasses import dataclass, field
from apps.next_period_high_low.container import NextPeriodHighLowContainer
from apps.next_period_high_low.config import NextPeriodHighLowConfig

from core.utils.command import CommandSession
from core.utils.container.command import ContainerCommandSession

@dataclass
class RunStrategyCommandSession(
	ContainerCommandSession,
	CommandSession
):
	config: NextPeriodHighLowConfig = None
	container: NextPeriodHighLowContainer = None

	def run(self):
		super().run()
		self.config.dataset.batch_size = 1
		strategy = self.container.strategy()
		strategy.run()
