from core.utils.config import Config, dataclass

@dataclass
class HyperbandTunerConfig(Config):
	max_epochs: int = 10
	reduction_factor: int = 3
	iterations: int = 100
