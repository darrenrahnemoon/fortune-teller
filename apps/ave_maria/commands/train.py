from dataclasses import dataclass, field
from apps.ave_maria.container import AveMariaContainer
from apps.ave_maria.config import AveMariaConfig

from core.utils.cls.repr import pretty_repr
from core.utils.command import CommandSession
from core.utils.container.command import ContainerCommandSessionMixin

@dataclass
class TrainModelCommandSession(
	ContainerCommandSessionMixin,
	CommandSession
):
	config: AveMariaConfig = field(default_factory = AveMariaConfig)
	container: AveMariaContainer = None

	def setup(self):
		super().setup()

	def run(self):
		super().run()

		tensorflow_container = self.container.tensorflow()
		tuner_service = tensorflow_container.tuner_service()
		trainer_service = tensorflow_container.trainer_service()

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