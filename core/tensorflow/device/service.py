import tensorflow
from dataclasses import dataclass
from core.tensorflow.device.config import DeviceConfig

@dataclass
class DeviceService:
	config: DeviceConfig

	@property
	def selected(self):
		"""Used as a context manager to enable tensorflow to use the specified device"""
		device = self.get()
		return tensorflow.device(device.name)

	def get(self):
		if self.config.use == 'GPU':
			physical_device = tensorflow.config.list_physical_devices(self.config.use)[0]
			tensorflow.config.experimental.set_memory_growth(physical_device, True)
		logical_device = tensorflow.config.list_logical_devices(self.config.use)[0]
		return logical_device