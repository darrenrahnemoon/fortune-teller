import numpy

from dataclasses import dataclass, field
from keras.utils.data_utils import Sequence
from multiprocess import Process, Queue
from multiprocess.shared_memory import SharedMemory
from multiprocess.managers import SharedMemoryManager

from .kwargs import sequence_dataclass_kwargs

class GarbageCollectedSharedMemory(SharedMemory):
	def __del__(self):
		super().__del__()
		self.unlink()

class SharedMemoryNumpyArray(numpy.ndarray):
	def __new__(cls, *args, shared_memory = None, **kwargs):
		obj = super(SharedMemoryNumpyArray, cls).__new__(cls, *args, **kwargs)
		obj.shared_memory = shared_memory
		return obj

	def __array_finalize__(self, obj):
		if obj is None: return
		self.shared_memory = getattr(obj, 'shared_memory', None)

@dataclass(**sequence_dataclass_kwargs)
class SharedMemorySequence(Sequence):
	sequence: Sequence = None
	workers: int = 3
	max_queue_size: int = 8

	manager: SharedMemoryManager = field(init = False, default = None)
	processes: list[Process] = field(init = False, default = None)
	queue: Queue = field(init = False, default = None)

	def __len__(self):
		return len(self.sequence)

	def __getitem__(self, index):
		def convert_from_address_book(address_book) -> dict[str, dict or list or SharedMemoryNumpyArray]:
			if address_book['_type'] == 'numpy':
				shared_memory = GarbageCollectedSharedMemory(
					name = address_book['_name'],
				)
				shared_array = SharedMemoryNumpyArray(
					shape = address_book['_shape'],
					dtype = address_book['_dtype'],
					buffer = shared_memory.buf,
					offset = 0,
					shared_memory = shared_memory
				)
				return shared_array

			if address_book['_type'] == 'list':
				return [
					convert_from_address_book(item)
					for item in address_book['_items']
				]
			
			if address_book['_type'] == 'tuple':
				return tuple(
					convert_from_address_book(item)
					for item in address_book['_items']
				)

			if address_book['_type'] == 'dict':
				return {
					key : convert_from_address_book(value)
					for key, value in address_book.items()
					if key != '_type' # Skip the type indicator
				}

			raise Exception(f'Could not parse address book {address_book}')

		self.ensure_workers_initialized()
		item = self.queue.get(block = True)
		item = convert_from_address_book(item)
		return item['x'], item['y']

	def __del__(self):
		self.ensure_workers_destroyed()

	@staticmethod
	def worker(
		manager: SharedMemoryManager = None,
		sequence: Sequence = None,
		queue: Queue = None,
		indices: list[int] = None,
	):
		def convert_numpy_array_to_shared_memory(data: numpy.ndarray):
			shared_memory = manager.SharedMemory(
				size = data.nbytes
			)
			shared_array = numpy.ndarray(
				shape = data.shape,
				dtype = data.dtype,
				buffer = shared_memory.buf,
				offset = 0
			)
			shared_array[:] = data[:]
			return shared_array, shared_memory

		def convert_to_memory_address_book(data: list or numpy.ndarray or dict[str, dict or numpy.ndarray]):
			if type(data) == numpy.ndarray:
				shared_array, shared_memory = convert_numpy_array_to_shared_memory(data)
				return {
					'_type' : 'numpy',
					'_name' : shared_memory.name,
					'_shape': shared_array.shape,
					'_dtype': shared_array.dtype,
				}

			if type(data) == list:
				return {
					'_type': 'list',
					'_items': [
						convert_to_memory_address_book(item)
						for item in data
					]
				}

			if type(data) == tuple:
				return {
					'_type': 'tuple',
					'_items': [
						convert_to_memory_address_book(item)
						for item in data
					]
				}

			if type(data) == dict:
				address = {
					key : convert_to_memory_address_book(value)
					for key, value in data.items()
				}
				address['_type'] = 'dict'
				return address

			raise Exception(f'Unrecognized type to share between processes {type(data)}')

		for index in indices:
			x, y = sequence[index]
			item = {
				'x' : x,
				'y' : y,
			}
			item = convert_to_memory_address_book(item)
			queue.put(item)

	def ensure_workers_initialized(self):
		if self.manager != None:
			return

		self.manager = SharedMemoryManager()
		self.manager.start()
		self.queue = Queue(maxsize = self.max_queue_size)

		indices_batches = numpy.array_split(numpy.arange(len(self)), self.workers)
		self.processes = [
			Process(
				target = self.worker,
				kwargs = {
					'sequence': self.sequence,
					'manager': self.manager,
					'queue': self.queue,
					'indices': indices_batch
				},
			)
			for indices_batch in indices_batches
		]
		for process in self.processes:
			process.start()

	def ensure_workers_destroyed(self):
		if self.processes:
			for process in self.processes:
				process.close()
				process.join()
			self.processes = None
		if self.manager:
			self.manager.shutdown()
			self.manager.join()
			self.manager = None
		if self.queue:
			self.queue.close()
			self.queue = None
