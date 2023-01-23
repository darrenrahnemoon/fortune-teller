from typing import Callable
from dataclasses import dataclass
from pathlib import Path

import tensorflow
from keras.callbacks import EarlyStopping, ModelCheckpoint, TensorBoard
from keras_tuner import Hyperband

from core.chart import ChartGroup
from .model import NextPeriodHighLowModel
from .preprocessor import NextPeriodHighLowPreprocessor
from .sequence import NextPeriodHighLowSequence
from core.utils.time import TimestampLike, now
from core.tensorflow.sequence import ShuffledSequence, PartialSequence, BatchedSequence, SharedMemorySequence

@dataclass
class NextPeriodHighLowService:
	build_input_chart_group: Callable[..., ChartGroup] = None
	build_output_chart_group: Callable[..., ChartGroup] = None
	forward_window_length: int = None
	backward_window_length: int = None

	validation_split: float = None
	batch_size: int = None
	epochs: int = None
	steps_per_epoch: int = None
	use_multiprocessing: bool = None
	max_queue_size: int = None
	workers: int = None
	use_device: str = None
	hyperband_max_epochs: int = None
	hyperband_reduction_factor: int = None
	hyperband_iterations: int = None

	preprocessor: NextPeriodHighLowPreprocessor = None
	model: NextPeriodHighLowModel = None
	dataset: NextPeriodHighLowSequence = None

	@property
	def tensorboard_directory(self):
		return Path(__file__).parent.joinpath('artifacts/tensorboard')

	@property
	def keras_tuner_directory(self):
		return Path(__file__).parent.joinpath('artifacts/tuner')

	@property
	def training_checkpoints_directory(self):
		return Path(__file__).parent.joinpath('artifacts/checkpoints/checkpoints')

	def get_callbacks(self):
		return [
			EarlyStopping(monitor = 'val_loss', patience = 5),
			TensorBoard(log_dir = self.tensorboard_directory)
		]

	def predict(self, timestamp: TimestampLike = now()):
		model = self.get_best_model()
		input_chart_group = self.build_input_chart_group()
		input_chart_group.read(to_timestamp = timestamp)
		self.preprocessor.process_input(input_chart_group, truncate_from = 'tail')
		return input_chart_group.dataframe

	def get_tuner(self):
		return Hyperband(
			hypermodel = self.model.build,
			objective = 'val_loss',
			max_epochs = self.hyperband_max_epochs,
			hyperband_iterations = self.hyperband_iterations,
			factor = self.hyperband_reduction_factor,
			directory = self.keras_tuner_directory,
			project_name = 'trials'
		)

	def tune_model(self):
		training_dataset, validation_dataset = self.get_datasets()
		device = self.get_device()
		tuner = self.get_tuner()

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
				callbacks = self.get_callbacks()
			)

	def get_best_model(self):
		tuner = self.get_tuner()
		parameters = tuner.get_best_hyperparameters(1)[0]
		model = self.model.build(parameters)

		if self.training_checkpoints_directory.exists():
			model.load_weights(self.training_checkpoints_directory)

		return model

	def train_model(self):
		training_dataset, validation_dataset = self.get_datasets()
		device = self.get_device()
		model = self.get_best_model()
		model.summary()

		with tensorflow.device(device.name):
			model.fit(
				x = training_dataset,
				validation_data = validation_dataset,
				epochs = self.epochs,
				steps_per_epoch = self.steps_per_epoch,
				batch_size = self.batch_size,
				validation_batch_size = self.batch_size,
				validation_steps = int(self.steps_per_epoch / (1 - self.validation_split) * self.validation_split),
				verbose = True,
				callbacks = [
					*self.get_callbacks(),
					ModelCheckpoint(
						filepath = self.training_checkpoints_directory,
						save_weights_only = True,
						monitor = 'val_accuracy',
						mode = 'max',
						save_best_only = True,
					)
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