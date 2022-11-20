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

	def setup(self):
		pass

	def cleanup(self):
		pass

	def handler(self):
		pass

	def abort(self):
		self.is_aborted = True
		self.cleanup()