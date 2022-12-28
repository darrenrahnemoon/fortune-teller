import numpy
import atexit
from dataclasses import dataclass
from keras.utils.data_utils import Sequence
from multiprocess import Process, Queue, shared_memory, managers

class ErasingSharedMemory(shared_memory.SharedMemory):
	def __del__(self):
		super(ErasingSharedMemory, self).__del__()
		self.unlink()

class SharedMemoryArray(numpy.ndarray):
	def __new__(cls, *args, shm = None, **kwargs):
		obj = super(SharedMemoryArray, cls).__new__(cls, *args, **kwargs)
		obj.shm = shm
		return obj

	def __array_finalize__(self, obj):
		if obj is None: return
		self.shm = getattr(obj, 'shm', None)

@dataclass
class SharedMemoryGenerator:
	manager = None

	@classmethod
	def worker(self, sequence: Sequence, indices, queue):
		for index in indices:
			x, y = sequence[index]

			shm = self.manager.SharedMemory(size = x.nbytes + y.nbytes)
			shared_x = numpy.ndarray(x.shape, dtype = x.dtype, buffer = shm.buf, offset = 0)
			shared_y = numpy.ndarray(y.shape, dtype = y.dtype, buffer = shm.buf, offset = x.nbytes)

			shared_x[:] = x[:]
			shared_y[:] = y[:]

			queue.put((shared_x.shape, shared_x.dtype, shared_y.shape, shared_y.dtype, shm.name))
			shm.close()
			del shm

	@classmethod
	def to_generator(
		self,
		sequence: Sequence,
		workers = 2,
		max_queue_size = 2
	):
		queue = Queue(maxsize = max_queue_size)

		if self.manager == None:
			self.manager = managers.SharedMemoryManager()
			self.manager.start()

		indices = numpy.array_split(numpy.arange(len(sequence)), workers)
		processes = [
			Process(
				target = self.worker,
				args = (sequence, indices, queue)
			)
			for indices in indices
		]
		for process in processes:
			process.start()

		try:
			for _ in range(len(sequence)):
				x_shape, x_dtype, y_shape, y_dtype, shm_name = queue.get(block = True)
				existing_shm = ErasingSharedMemory(name = shm_name)
				x = SharedMemoryArray(x_shape, dtype = x_dtype, buffer = existing_shm.buf, offset = 0, shm = existing_shm)
				y = SharedMemoryArray(y_shape, dtype = y_dtype, buffer = existing_shm.buf, offset = x.nbytes, shm = existing_shm)
				yield x, y
		except KeyboardInterrupt:
			self.close()
		finally:
			for process in processes:
				process.terminate()
			for process in processes:
				process.join()
			queue.close()

	@staticmethod
	@atexit.register
	def close():
		if SharedMemoryGenerator.manager:
			SharedMemoryGenerator.manager.shutdown()
			SharedMemoryGenerator.manager.join()
