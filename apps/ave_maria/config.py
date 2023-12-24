from dataclasses import field, dataclass
from core.utils.config import Config
from .trading.config import AveMariaTradingConfig
from .tensorflow.config import AveMariaTensorflowConfig

@dataclass
class AveMariaConfig(Config):
	trading: AveMariaTradingConfig = field(default_factory=AveMariaTradingConfig)
	tensorflow: AveMariaTensorflowConfig = field(default_factory=AveMariaTensorflowConfig)