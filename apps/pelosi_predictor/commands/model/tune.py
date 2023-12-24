from dataclasses import dataclass, field
from apps.pelosi_predictor.container import PelosiPredictorContainer
from apps.pelosi_predictor.config import PelosiPredictorConfig

from core.utils.command import CommandSession
from core.utils.container.command import ContainerCommandSession

@dataclass
class TuneModelCommandSession(
	ContainerCommandSession,
	CommandSession
):
	config: PelosiPredictorConfig = field(default_factory = PelosiPredictorConfig)
	container: PelosiPredictorContainer = None

	def setup(self):
		super().setup()

	def run(self):
		super().run()
		model_container = self.container.model()
		tuner_service = model_container.tuner_service()
		tuner_service.tune()