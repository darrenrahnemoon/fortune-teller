from argparse import BooleanOptionalAction
from dataclasses import dataclass, field
from examples.ave_maria.container import AveMariaContainer
from examples.ave_maria.config import AveMariaConfig

from core.utils.os import open_file
from core.utils.command import CommandSession
from core.utils.container.command import ContainerCommandSessionMixin

@dataclass
class ViewModelCommandSession(
	ContainerCommandSessionMixin,
	CommandSession
):
	config: AveMariaConfig = field(default_factory = AveMariaConfig)
	container: AveMariaContainer = None

	def setup(self):
		super().setup()
		self.parser.add_argument('--trial', default = 'best')
		self.parser.add_argument('--plot', action = BooleanOptionalAction)

	def run(self):
		super().run()
		tensorflow_container = self.container.tensorflow()
		tuner_service = tensorflow_container.tuner_service()
		trainer_service = tensorflow_container.trainer_service()
		model = tuner_service.get_model(self.args.trial)
		model.summary()

		if self.args.plot:
			trainer_service.plot(model)
			path = trainer_service.get_plot_path(model)
			open_file(path)