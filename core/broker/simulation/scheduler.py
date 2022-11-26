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
		self.queue.append((
			timestamp,
			functools.partial(action, *args, **kwargs)
		))

	def run_as_of(self, now):
		self.queue.sort(key=lambda item: item[0])
		to_run, to_defer = [], []
		for item in self.queue:
			if item[0] <= now:
				to_run.append(item)
			else:
				to_defer.append(item)
		self.queue = to_defer
		for _, action in to_run:
			action()