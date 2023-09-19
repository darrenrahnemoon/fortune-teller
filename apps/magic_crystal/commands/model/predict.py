import pandas

from argparse import BooleanOptionalAction
from dataclasses import dataclass, field
from apps.magic_crystal.container import MagicCrystalContainer
from apps.magic_crystal.preprocessor.prediction import MagicCrystalPrediction
from apps.magic_crystal.config import MagicCrystalConfig

from core.utils.command import CommandSession
from core.utils.time import now, normalize_timestamp
from core.utils.collection.command import ListOutputFormatCommandSession
from core.utils.container.command import ContainerCommandSession

@dataclass
class PredictModelCommandSession(
	ContainerCommandSession,
	ListOutputFormatCommandSession,
	CommandSession
):
	config: MagicCrystalConfig = field(default_factory = MagicCrystalConfig)
	container: MagicCrystalContainer = None

	def setup(self):
		super().setup()
		self.parser.add_argument('--evaluate', action = BooleanOptionalAction)
		self.parser.add_argument('--prompt', '-p', action = BooleanOptionalAction)
		self.parser.add_argument('--timestamp', type = normalize_timestamp, default = now())

	def run(self):
		super().run()
		self.config.dataset.batch_size = 1

		model_container = self.container.model()
		tuner_service = model_container.tuner_service()
		trainer_service = model_container.trainer_service()
		self.predictor_service = model_container.predictor_service()

		self.model = tuner_service.get_model(self.config.trainer.trial)
		trainer_service.load_weights(self.model)

		if self.args.prompt:
			while True:
				timestamp = input('Timestamp: ')
				timestamp = normalize_timestamp(timestamp)
				self.predict(timestamp)
		else:
			self.predict(self.args.timestamp)

	def predict(self, timestamp: pandas.Timestamp):
		predictions = (getattr(self.predictor_service, 'evaluate' if self.args.evaluate else 'predict'))(
			model = self.model,
			timestamp = timestamp,
		)
		self.print_list(predictions, MagicCrystalPrediction)