from dataclasses import dataclass, field
from apps.next_period_high_low.container import NextPeriodHighLowContainer
from apps.next_period_high_low.config import NextPeriodHighLowConfig

from core.utils.command import CommandSession
from core.utils.container.command import ContainerCommandSession

@dataclass
class TuneModelCommandSession(
	ContainerCommandSession,
	CommandSession
):
	config: NextPeriodHighLowConfig = field(default_factory = NextPeriodHighLowConfig)
	container: NextPeriodHighLowContainer = None

	def setup(self):
		super().setup()
		self.parser.add_argument('model')

	def run(self):
		super().run()
		container = getattr(self.container, self.args.model)()
		tuner_service = container.tuner_service()
		tuner_service.tune()