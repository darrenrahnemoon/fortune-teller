from argparse import BooleanOptionalAction
from dataclasses import dataclass, field
from apps.next_period_high_low.container import NextPeriodHighLowContainer
from apps.next_period_high_low.config import NextPeriodHighLowConfig

from core.utils.os import open_file
from core.utils.command import CommandSession
from core.utils.container.command import ContainerCommandSession

@dataclass
class ViewModelCommandSession(
	ContainerCommandSession,
	CommandSession
):
	config: NextPeriodHighLowConfig = field(default_factory = NextPeriodHighLowConfig)
	container: NextPeriodHighLowContainer = None

	def setup(self):
		super().setup()
		self.parser.add_argument('model')
		self.parser.add_argument('trial', default = 'best')
		self.parser.add_argument('--plot', action = BooleanOptionalAction)

	def run(self):
		super().run()
		container = getattr(self.container, self.args.model)()

		tuner_service = container.tuner_service()
		trainer_service = container.trainer_service()
		model = tuner_service.get_model(self.args.trial)
		model.summary()

		if self.args.plot:
			trainer_service.plot(model)
			path = trainer_service.get_plot_path(model)
			open_file(path)