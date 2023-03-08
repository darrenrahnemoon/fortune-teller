from core.utils.config import Config, dataclass

@dataclass
class TensorboardConfig(Config):
	enabled: bool = False
	overwrite: bool = False
