import typing
import functools
import pandas

class Scheduler:
	def __init__(self):
		self.queue = []

	def add(
		self,
		action: typing.Callable = None,
		timestamp: pandas.Timestamp = None,
		args = [],
		kwargs = {},
	):
		self.queue.append({
			'timestamp': timestamp,
			'action': functools.partial(action, *args, **kwargs)
		})

	def run_as_of(self, now: pandas.Timestamp):
		self.queue.sort(key = lambda item: item['timestamp'])
		to_run, to_defer = [], []
		for item in self.queue:
			if item['timestamp'] <= now:
				to_run.append(item)
			else:
				to_defer.append(item)
		self.queue = to_defer
		for item in to_run:
			item['action']()