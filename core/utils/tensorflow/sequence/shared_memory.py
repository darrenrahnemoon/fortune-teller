import numpy

from dataclasses import dataclass, field
from keras.utils.data_utils import Sequence
from multiprocess import Process, Queue, shared_memory, managers

from .kwargs import sequence_dataclass_kwargs

class ErasingSharedMemory(shared_memory.SharedMemory):
	def __del__(self):
		super(ErasingSharedMemory, self).__del__()
		self.unlink()

class ShareableNumpyArray(numpy.ndarray):
	def __new__(cls, *args, shm = None, **kwargs):
		obj = super(ShareableNumpyArray, cls).__new__(cls, *args, **kwargs)
		obj.shm = shm
		return obj

	def __array_finalize__(self, obj):
		if obj is None: return
		self.shm = getattr(obj, 'shm', None)

@dataclass(**sequence_dataclass_kwargs)
class SharedMemorySequence(Sequence):
	sequence: Sequence = None
	workers: int = 3
	max_queue_size: int = 8

	manager: managers.SharedMemoryManager = field(init = False, default = None)
	processes: list[Process] = field(init = False, default = None)
	queue: Queue = field(init = False, default = None)

	def __len__(self):
		return len(self.sequence)

	def __getitem__(self, index):
		self.ensure_workers_initialized()
		queue_item = self.queue.get(block = True)
		existing_shm = ErasingSharedMemory(name = queue_item['name'])

		x = ShareableNumpyArray(
			shape = queue_item['x']['shape'],
			dtype = queue_item['x']['dtype'],
			buffer = existing_shm.buf,
			offset = 0,
			shm = existing_shm
		)
		y = ShareableNumpyArray(
			shape = queue_item['y']['shape'],
			dtype = queue_item['y']['dtype'],
			buffer = existing_shm.buf,
			offset = x.nbytes,
			shm = existing_shm
		)
		return x, y

	def __del__(self):
		self.ensure_workers_destroyed()

	@staticmethod
	def worker(
		manager: managers.SharedMemoryManager = None,
		sequence: Sequence = None,
		queue: Queue = None,
		indices: list[int] = None,
	):
		for index in indices:
			x, y = sequence[index]
			shm = manager.SharedMemory(size = x.nbytes + y.nbytes)
			shared_x = numpy.ndarray(x.shape, dtype = x.dtype, buffer = shm.buf, offset = 0)
			shared_y = numpy.ndarray(y.shape, dtype = y.dtype, buffer = shm.buf, offset = x.nbytes)
			shared_x[:] = x[:]
			shared_y[:] = y[:]

			queue.put({
				'name': shm.name,
				'x': {
					'shape': shared_x.shape,
					'dtype': shared_x.dtype,
				},
				'y': {
					'shape': shared_y.shape,
					'dtype': shared_y.dtype
				}
			})
			shm.close()
			del shm

	def ensure_workers_initialized(self):
		if self.manager != None:
			return

		self.manager = managers.SharedMemoryManager()
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
				process.terminate()
				process.join()
			self.processes = None
		if self.manager:
			self.manager.shutdown()
			self.manager.join()
			self.manager = None
		if self.queue:
			self.queue.close()
			self.queue = None
