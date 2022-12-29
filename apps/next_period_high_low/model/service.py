from typing import Callable
from dataclasses import dataclass, field
from pathlib import Path

import tensorflow
from keras.callbacks import EarlyStopping, TensorBoard
from keras_tuner import Hyperband

from core.chart import ChartGroup
from .model import NextPeriodHighLowModel
from .preprocessor import NextPeriodHighLowPreprocessor
from .repository import NextPeriodHighLowRepository
from .sequence import NextPeriodHighLowSequence
from core.utils.tensorflow.sequence import ShuffledSequence, PartialSequence, BatchedSequence, SharedMemorySequence

@dataclass
class NextPeriodHighLowService:
	build_input_chart_group: Callable[..., ChartGroup] = None
	build_output_chart_group: Callable[..., ChartGroup] = None

	forward_window_length: int = None
	backward_window_length: int = None

	validation_split: float = 0.3
	batch_size: int = 2
	epochs: int = 50
	steps_per_epoch: int = 20
	hyperband_max_epochs: int = 10
	hyperband_reduction_factor: int = 3
	hyperband_iterations: int = 100
	use_multiprocessing: bool = True
	max_queue_size: int = 10
	workers: int = 5
	use_device: str = 'CPU'

	repository: NextPeriodHighLowRepository = field(init = False)
	preprocessor: NextPeriodHighLowPreprocessor = field(init = False)
	model: NextPeriodHighLowModel = field(init = False)
	dataset: NextPeriodHighLowSequence = field(init = False)

	@property
	def tensorboard_directory(self):
		return Path(__file__).parent.joinpath('artifacts/tensorboard')

	@property
	def keras_tuner_directory(self):
		return Path(__file__).parent.joinpath('artifacts/tuner')

	def tune_model(self):
		training_dataset, validation_dataset = self.get_datasets()
		device = self.get_device()

		tuner = Hyperband(
			hypermodel = self.model.build,
			objective = 'val_loss',
			max_epochs = self.hyperband_max_epochs,
			hyperband_iterations = self.hyperband_iterations,
			factor = self.hyperband_reduction_factor,
			directory = self.keras_tuner_directory,
			project_name = 'trials'
		)

		with tensorflow.device(device.name):
			tuner.search(
				x = training_dataset,
				validation_data = validation_dataset,
				epochs = self.epochs,
				steps_per_epoch = self.steps_per_epoch,
				batch_size = self.batch_size,
				validation_batch_size = self.batch_size,
				validation_steps = int(self.steps_per_epoch / (1 - self.validation_split) * self.validation_split),
				verbose = True,
				callbacks = [
					EarlyStopping(monitor = 'val_loss', patience = 5),
					TensorBoard(log_dir = self.tensorboard_directory)
				]
			)

	def get_device(self):
		if self.use_device == 'GPU':
			physical_device = tensorflow.config.list_physical_devices(self.use_device)[0]
			tensorflow.config.experimental.set_memory_growth(physical_device, True)
		logical_device = tensorflow.config.list_logical_devices(self.use_device)[0]
		return logical_device

	def get_datasets(self):
		# Dataset
		dataset = ShuffledSequence(self.dataset)

		# Training Dataset
		training_dataset = PartialSequence(
			sequence = dataset,
			portion = 1 - self.validation_split
		)
		training_dataset = BatchedSequence(
			sequence = training_dataset,
			batch_size = self.batch_size
		)
		if self.use_multiprocessing:
			training_dataset = SharedMemorySequence(
				sequence = training_dataset,
				workers = self.workers,
				max_queue_size = self.max_queue_size
			)

		# Validation Dataset
		validation_dataset = PartialSequence(
			sequence = dataset,
			offset = 1 - self.validation_split,
			portion = self.validation_split
		)
		validation_dataset = BatchedSequence(
			sequence = validation_dataset,
			batch_size = self.batch_size
		)
		if self.use_multiprocessing:
			validation_dataset = SharedMemorySequence(
				sequence = validation_dataset,
				workers = self.workers,
				max_queue_size = self.max_queue_size
			)
		return training_dataset, validation_dataset

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

		self.dataset = NextPeriodHighLowSequence(
			build_input_chart_group = self.build_input_chart_group,
			build_output_chart_group = self.build_output_chart_group,
			forward_window_length = self.forward_window_length,
			backward_window_length = self.backward_window_length,
			repository = self.repository,
			preprocessor = self.preprocessor
		)
