from core.utils.config import Config, dataclass

@dataclass
class TensorboardConfig(Config):
	enabled: bool = False
	overwrite: bool = False
	debugger_enabled: bool = False

	histogram_frequency: int = 0
	write_steps_per_second: bool = True
	write_images: bool = True 