from dataclasses import dataclass
from keras.utils.data_utils import Sequence

from .kwargs import sequence_dataclass_kwargs

@dataclass(**sequence_dataclass_kwargs)
class SkippableSequence(Sequence):
	sequence: Sequence = None
	offset: int = 0

	def __getitem__(self, index):
		item = self.sequence[index + self.offset]
		if type(item) == type(None):
			self.offset += 1
			return self[index]
		return item

	def __len__(self):
		return len(self.sequence)