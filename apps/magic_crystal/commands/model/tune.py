from dataclasses import dataclass, field
from apps.magic_crystal.container import MagicCrystalContainer
from apps.magic_crystal.config import MagicCrystalConfig

from core.utils.command import CommandSession
from core.utils.container.command import ContainerCommandSession

@dataclass
class TuneModelCommandSession(
	ContainerCommandSession,
	CommandSession
):
	config: MagicCrystalConfig = field(default_factory = MagicCrystalConfig)
	container: MagicCrystalContainer = None

	def setup(self):
		super().setup()

	def run(self):
		super().run()
		model_container = self.container.model()
		tuner_service = model_container.tuner_service()
		tuner_service.tune()