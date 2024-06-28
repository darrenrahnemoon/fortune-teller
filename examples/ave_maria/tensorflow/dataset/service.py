from dataclasses import dataclass
from keras.utils.data_utils import Sequence

from core.tensorflow.dataset.service import DatasetService
from core.tensorflow.dataset.sequence.shared_memory import SharedMemorySequence
from core.tensorflow.dataset.sequence.batched import BatchedSequence
from core.tensorflow.dataset.sequence.partial import PartialSequence
from core.tensorflow.dataset.sequence.shuffled import ShuffledSequence
from core.tensorflow.dataset.sequence.skippable import SkippableSequence

from apps.ave_maria.trading.config import AveMariaTradingConfig
from apps.ave_maria.tensorflow.preprocessor.service import AveMariaPreprocessorService
from apps.ave_maria.tensorflow.dataset.sequence import AveMariaSequence

@dataclass
class AveMariaDatasetService(DatasetService):
	preprocessor_service: AveMariaPreprocessorService = None
	trading_config: AveMariaTradingConfig = None
	sequence: Sequence = None

	def __post_init__(self):
		self.sequence = AveMariaSequence(
			trading_config = self.trading_config,
			preprocessor_service = self.preprocessor_service,
		)

	def build(self) -> tuple[Sequence, Sequence]:
		# Dataset
		dataset = self.sequence
		dataset = ShuffledSequence(dataset)
		dataset = SkippableSequence(dataset)

		# Training Dataset
		training_dataset = PartialSequence(
			sequence = dataset,
			portion = 1 - self.config.validation_split
		)
		training_dataset = BatchedSequence(
			sequence = training_dataset,
			batch_size = self.config.batch_size
		)
		if self.config.use_multiprocessing:
			training_dataset = SharedMemorySequence(
				sequence = training_dataset,
				workers = self.config.workers,
				max_queue_size = self.config.max_queue_size
			)

		# Validation Dataset
		validation_dataset = PartialSequence(
			sequence = dataset,
			offset = 1 - self.config.validation_split,
			portion = self.config.validation_split
		)
		validation_dataset = BatchedSequence(
			sequence = validation_dataset,
			batch_size = self.config.batch_size
		)
		if self.config.use_multiprocessing:
			validation_dataset = SharedMemorySequence(
				sequence = validation_dataset,
				workers = self.config.workers,
				max_queue_size = self.config.max_queue_size
			)
		return training_dataset, validation_dataset
