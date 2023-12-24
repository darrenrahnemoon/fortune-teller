from argparse import BooleanOptionalAction
from dataclasses import dataclass, field
from apps.pelosi_predictor.container import PelosiPredictorContainer
from apps.pelosi_predictor.config import PelosiPredictorConfig

from core.utils.os import open_file
from core.utils.command import CommandSession
from core.utils.container.command import ContainerCommandSession

@dataclass
class ViewModelCommandSession(
	ContainerCommandSession,
	CommandSession
):
	config: PelosiPredictorConfig = field(default_factory = PelosiPredictorConfig)
	container: PelosiPredictorContainer = None

	def setup(self):
		super().setup()
		self.parser.add_argument('trial', default = 'best')
		self.parser.add_argument('--plot', action = BooleanOptionalAction)

	def run(self):
		super().run()
		model_container = self.container.model()
		tuner_service = model_container.tuner_service()
		trainer_service = model_container.trainer_service()
		model = tuner_service.get_model(self.args.trial)
		model.summary()

		if self.args.plot:
			trainer_service.plot(model)
			path = trainer_service.get_plot_path(model)
			open_file(path)