from dataclasses import field, dataclass
from core.utils.config import Config
from .action import AveMariaActionConfig
from .observation import AveMariaObservationConfig

@dataclass
class AveMariaTradingConfig(Config):
	action: AveMariaActionConfig = field(default_factory=AveMariaActionConfig)
	observation: AveMariaObservationConfig = field(default_factory=AveMariaObservationConfig)