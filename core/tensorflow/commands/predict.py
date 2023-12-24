import pandas

from argparse import BooleanOptionalAction
from dataclasses import dataclass
from typing import ClassVar, Type

from core.tensorflow.preprocessor.prediction import Prediction
from core.utils.container import DeclarativeContainer
from core.utils.config import Config
from core.utils.command import CommandSession
from core.utils.time import now, normalize_timestamp
from core.utils.collection.command import ListOutputFormatCommandSessionMixin
from core.utils.container.command import ContainerCommandSessionMixin

@dataclass
class PredictCommandSession(
	ContainerCommandSessionMixin,
	ListOutputFormatCommandSessionMixin,
	CommandSession
):
	config: Config = None
	container: DeclarativeContainer = None
	prediction_class: ClassVar[Type[Prediction]] = None

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
		self.print_list(predictions, self.prediction_class)