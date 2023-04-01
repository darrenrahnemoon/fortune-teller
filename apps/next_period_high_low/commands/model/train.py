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
		container = getattr(self.container, self.args.model)()
		tuner_service = container.tuner_service()
		trainer_service = container.trainer_service()

		# Print Model
		model = tuner_service.get_model(trainer_service.config.trial)
		model.summary()

		# Print Hyperparameters
		hyperparameters = tuner_service.get_hyperparameters(trainer_service.config.trial)
		print(pretty_repr(hyperparameters.values))

		trainer_service.train(
			model = model,
			hyperparameters = hyperparameters
		)