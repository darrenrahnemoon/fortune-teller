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

		inputs = self.convert_potential_list_of_dicts_to_dict_of_lists(inputs)
		outputs = self.convert_potential_list_of_dicts_to_dict_of_lists(outputs)

		return inputs, outputs

	def convert_potential_list_of_dicts_to_dict_of_lists(self, data):
		if type(data[0]) == dict:
			return {
				key : numpy.stack([
					item[key]
					for item in data
				])
				for key in data[0]
			}
		return data
