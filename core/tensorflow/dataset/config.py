from dataclasses import field
from core.utils.config import Config, dataclass, on_stage

@dataclass
class DatasetConfig(Config):
	batch_size: int = field(
		default_factory = lambda : on_stage(
			development = 2,
			production = 1,
		)
	)
	validation_split: float = 0.3
	max_queue_size: int = 10
	workers: int = 5
	use_multiprocessing: bool = True