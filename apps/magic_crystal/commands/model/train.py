from dataclasses import dataclass, field
from apps.magic_crystal.container import MagicCrystalContainer
from apps.magic_crystal.config import MagicCrystalConfig

from core.utils.cls.repr import pretty_repr
from core.utils.command import CommandSession
from core.utils.container.command import ContainerCommandSession

@dataclass
class TrainModelCommandSession(
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
		trainer_service = model_container.trainer_service()

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