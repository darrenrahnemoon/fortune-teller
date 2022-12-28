from typing import Callable
from dataclasses import dataclass, field
from caseconverter import snakecase

import tensorflow

from keras.callbacks import EarlyStopping, TensorBoard
from keras.utils.data_utils import Sequence
from keras_tuner import Hyperband

from core.chart import ChartGroup
from .model import NextPeriodHighLowModel
from .preprocessor import NextPeriodHighLowPreprocessor
from .repository import NextPeriodHighLowRepository
from .sequence import NextPeriodHighLowSequence
from core.utils.environment import project_directory
from core.utils.tensorflow.sequence import ShuffledSequence, PartialSequence, BatchedSequence, SharedMemoryGenerator

gpu = tensorflow.config.list_physical_devices('GPU')
tensorflow.config.experimental.set_memory_growth(gpu[0], True)

@dataclass
class NextPeriodHighLowService:
	build_input_chart_group: Callable[..., ChartGroup] = None
	build_output_chart_group: Callable[..., ChartGroup] = None

	forward_window_length: int = None
	backward_window_length: int = None

	dataset: Sequence = field(init = False)
	training_dataset: Sequence = field(init = False)
	validation_dataset: Sequence = field(init = False)

	validation_split: float = 0.3
	batch_size: int = 2
	epochs: int = 50
	steps_per_epoch: int = 20
	hyperband_max_epochs: int = 10
	hyperband_reduction_factor: int = 3
	max_queue_size: int = 20
	workers: int = 5

	repository: NextPeriodHighLowRepository = field(init = False)
	preprocessor: NextPeriodHighLowPreprocessor = field(init = False)

	def tune_model(self):
		model_name = snakecase(type(self.model).__name__)
		tuner = Hyperband(
			hypermodel = self.model.build,
			objective = 'val_loss',
			max_epochs = self.hyperband_max_epochs,
			factor = self.hyperband_reduction_factor,
			directory = project_directory.joinpath('models/keras_tuner'),
			project_name = model_name
		)
		with tensorflow.device('/device:CPU:0'):
			tuner.search(
				self.training_generator,
				validation_data = self.validation_generator,
				epochs = self.epochs,
				steps_per_epoch = self.steps_per_epoch,
				batch_size = self.batch_size,
				validation_batch_size = self.batch_size,
				validation_steps = int(self.steps_per_epoch / (1 - self.validation_split) * self.validation_split),
				verbose = True,
				callbacks = [
					EarlyStopping(monitor = 'val_loss', patience = 5),
					TensorBoard(log_dir = project_directory.joinpath('models/tensorboard', model_name))
				]
			)

	def __post_init__(self):
		self.preprocessor = NextPeriodHighLowPreprocessor(
			forward_window_length = self.forward_window_length,
			backward_window_length = self.backward_window_length
		)
		self.repository = NextPeriodHighLowRepository(
			preprocessor = self.preprocessor
		)
		self.model = NextPeriodHighLowModel(
			build_input_chart_group = self.build_input_chart_group,
			build_output_chart_group = self.build_output_chart_group,
			forward_window_length = self.forward_window_length,
			backward_window_length = self.backward_window_length,
			batch_size = self.batch_size
		)

		# Dataset
		self.dataset = NextPeriodHighLowSequence(
			build_input_chart_group = self.build_input_chart_group,
			build_output_chart_group = self.build_output_chart_group,
			forward_window_length = self.forward_window_length,
			backward_window_length = self.backward_window_length,
			repository = self.repository,
			preprocessor = self.preprocessor
		)
		self.dataset = ShuffledSequence(self.dataset)

		# Training Dataset
		self.training_dataset = PartialSequence(
			sequence = self.dataset,
			portion = 1 - self.validation_split
		)
		self.training_dataset = BatchedSequence(
			sequence = self.training_dataset,
			batch_size = self.batch_size
		)
		self.training_generator = SharedMemoryGenerator.to_generator(
			self.training_dataset,
			workers = self.workers,
			max_queue_size = self.max_queue_size
		)

		# Validation Dataset
		self.validation_dataset = PartialSequence(
			sequence = self.dataset,
			offset = 1 - self.validation_split,
			portion = self.validation_split
		)
		self.validation_dataset = BatchedSequence(
			sequence = self.validation_dataset,
			batch_size = self.batch_size
		)
		self.validation_generator = SharedMemoryGenerator.to_generator(
			self.validation_dataset,
			workers = self.workers,
			max_queue_size = self.max_queue_size
		)

