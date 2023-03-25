from dataclasses import dataclass, field
from core.utils.config import Config

@dataclass
class ModelSizeConfig(Config):
	min: int = None
	max: int = None

@dataclass
class TunerConfig(Config):
	objective: str = 'val_loss'
	model_size: ModelSizeConfig = field(default_factory = ModelSizeConfig)