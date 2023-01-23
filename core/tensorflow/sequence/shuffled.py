import numpy
from dataclasses import dataclass, field
from keras.utils.data_utils import Sequence
from .kwargs import sequence_dataclass_kwargs

@dataclass(**sequence_dataclass_kwargs)
class ShuffledSequence(Sequence):
	sequence: Sequence
	indices: list[int] = field(init=False)

	def __len__(self):
		return len(self.indices)

	def __getitem__(self, index):
		return self.sequence[self.indices[index]]

	def __post_init__(self):
		self.shuffle()

	def shuffle(self):
		self.indices = numpy.arange(len(self.sequence))
		numpy.random.shuffle(self.indices)
