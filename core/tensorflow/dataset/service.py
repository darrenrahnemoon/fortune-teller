from dataclasses import dataclass
from keras.utils.data_utils import Sequence

from core.tensorflow.dataset.config import DatasetConfig

@dataclass
class DatasetService:
	config: DatasetConfig = None
	dataset: Sequence = None

	def build(self) -> tuple[Sequence, Sequence]:
		pass