import typing

if typing.TYPE_CHECKING:
	from lib.broker import Broker

class Strategy:
	def __init__(self,broker: 'Broker' = None,**kwargs):
		if broker:
			self.broker: 'Broker' = broker

		self.is_aborted = False
		for key, value in kwargs.items():
			setattr(self, key, value)

		self.setup()

	def __repr__(self) -> str:
		return f"{type(self).__name__}({', '.join([ f'{key}={repr(value)}' for key, value in self.__dict__.items() if value != None ])})"

	def setup(self):
		pass

	def cleanup(self):
		pass

	def handler(self):
		pass

	def abort(self):
		self.is_aborted = True
		self.cleanup()