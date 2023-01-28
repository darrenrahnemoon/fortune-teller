from core.utils.config import Config, dataclass

@dataclass
class TrainerConfig(Config):
	epochs: int = 100
	steps_per_epoch: int = 20