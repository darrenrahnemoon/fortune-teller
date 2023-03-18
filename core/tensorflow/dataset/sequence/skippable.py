from dataclasses import dataclass, field
from keras.utils.data_utils import Sequence

from .kwargs import sequence_dataclass_kwargs

class SkipItemException(Exception):
	pass

@dataclass(**sequence_dataclass_kwargs)
class SkippableSequence(Sequence):
	sequence: Sequence = None

	def __getitem__(self, index):
		try:
			return self.sequence[index]
		except SkipItemException:
			return self[index + 1]

	def __len__(self):
		return len(self.sequence)