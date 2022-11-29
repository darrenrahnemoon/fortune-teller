from core.utils.cls import instance_to_repr
import typing

if typing.TYPE_CHECKING:
	from core.broker import Broker

class Strategy:
	def __init__(self,broker: 'Broker' = None,**kwargs):
		if broker:
			self.broker: 'Broker' = broker

		self.is_aborted = False
		for key, value in kwargs.items():
			setattr(self, key, value)

		self.setup()

	def __repr__(self) -> str:
		return instance_to_repr(self, self.__dict__.keys())

	def setup(self):
		pass

	def cleanup(self):
		pass

	def handler(self):
		pass

	def abort(self):
		self.is_aborted = True
		self.cleanup()