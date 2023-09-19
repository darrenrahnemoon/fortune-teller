from argparse import ArgumentParser, Namespace

from dataclasses import dataclass, field
from apps.magic_crystal.container import MagicCrystalContainer
from apps.magic_crystal.config import MagicCrystalConfig

from core.utils.command import CommandSession
from core.utils.container.command import ContainerCommandSession

@dataclass
class RunStrategyCommandSession(
	ContainerCommandSession,
	CommandSession
):
	config: MagicCrystalConfig = None
	container: MagicCrystalContainer = None

	def run(self):
		super().run()
		self.config.dataset.batch_size = 1
		strategy = self.container.strategy()
		strategy.run()
