import pandas
import sys

from dataclass_csv import DataclassWriter
from argparse import BooleanOptionalAction
from dataclasses import dataclass, field
from apps.next_period_high_low.container import NextPeriodHighLowContainer
from apps.next_period_high_low.preprocessor.prediction import NextPeriodHighLowPrediction
from apps.next_period_high_low.config import NextPeriodHighLowConfig

from core.utils.command import CommandSession
from core.utils.time import now, normalize_timestamp
from core.utils.cls.repr import pretty_repr
from core.utils.container.command import ContainerCommandSession

@dataclass
class PredictModelCommandSession(
	ContainerCommandSession,
	CommandSession
):
	config: NextPeriodHighLowConfig = field(default_factory = NextPeriodHighLowConfig)
	container: NextPeriodHighLowContainer = None

	def setup(self):
		super().setup()
		self.parser.add_argument('--evaluate', action = BooleanOptionalAction)
		self.parser.add_argument('--prompt', '-p', action = BooleanOptionalAction)
		self.parser.add_argument('--timestamp', type = normalize_timestamp, default = now())
		self.parser.add_argument('--format', choices = [ 'csv', 'repr' ], default = 'csv')

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
		if self.args.format == 'csv':
			DataclassWriter(sys.stdout, predictions, NextPeriodHighLowPrediction).write()
		else:
			print(pretty_repr(predictions))