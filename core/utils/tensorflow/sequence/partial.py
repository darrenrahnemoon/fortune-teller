import math

from dataclasses import dataclass
from keras.utils.data_utils import Sequence
from .kwargs import sequence_dataclass_kwargs

@dataclass(**sequence_dataclass_kwargs)
class PartialSequence(Sequence):
	sequence: Sequence = None
	offset: float = 0 # in decimals indicating percentage i.e 0.7
	portion: float = 0 # in decimals indicating percentage i.e 0.3

	def __len__(self):
		return math.floor(len(self.sequence) * self.portion)

	def __getitem__(self, index):
		return self.sequence[self.index_offset + index]

	@property
	def index_offset(self):
		return math.floor(len(self.sequence) * self.offset) - 1 # arrays start from 0
