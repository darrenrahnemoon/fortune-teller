from dataclasses import dataclass, field
from apps.next_period_high_low.container import NextPeriodHighLowContainer
from apps.next_period_high_low.config import NextPeriodHighLowConfig

from core.utils.cls.repr import pretty_repr
from core.utils.command import CommandSession
from core.utils.container.command import ContainerCommandSession

@dataclass
class TrainModelCommandSession(
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
		container = getattr(container, self.container)()

		tuner_service = container.tuner_service()
		trainer_service = container.trainer_service()
		model = tuner_service.get_model(trainer_service.config.trial)
		model.summary()
		parameters = tuner_service.get_hyperparameters(trainer_service.config.trial)
		print(pretty_repr(parameters.values))
		trainer_service.compile(model, parameters)
		trainer_service.load_weights(model)
		trainer_service.train(model)