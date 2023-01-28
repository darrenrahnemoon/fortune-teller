from core.utils.config import Config, dataclass

@dataclass
class DatasetConfig(Config):
	batch_size: int = 2
	validation_split: float = 0.3
	max_queue_size: int = 10
	workers: int = 5
	use_multiprocessing: bool = True