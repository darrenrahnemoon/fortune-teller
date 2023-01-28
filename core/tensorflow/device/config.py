from core.utils.config import Config, dataclass

@dataclass
class DeviceConfig(Config):
	use: str = 'CPU'
