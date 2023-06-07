import numpy
from dataclasses import dataclass
from keras.utils.data_utils import Sequence
from .kwargs import sequence_dataclass_kwargs

@dataclass(**sequence_dataclass_kwargs)
class BatchedSequence(Sequence):
	sequence: Sequence = None
	batch_size: int = None

	def __len__(self):
		return len(self.sequence) // self.batch_size

	def __getitem__(self, index):
		start = index * self.batch_size
		end = start + self.batch_size
		inputs, outputs = [], []
		for batch_item_index in range(start, end):
			x, y = self.sequence[batch_item_index]
			inputs.append(x)
			outputs.append(y)

		inputs = self.normalize(inputs)
		outputs = self.normalize(outputs)

		return inputs, outputs

	def normalize(self, data):
		if type(data[0]) == dict:
			return {
				key : numpy.stack([
					item[key]
					for item in data
				])
				for key in data[0]
			}
		if type(data) == list:
			return numpy.array(data)
		return data
