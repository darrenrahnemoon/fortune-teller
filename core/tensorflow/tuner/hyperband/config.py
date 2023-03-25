from dataclasses import dataclass
from core.tensorflow.tuner.base.config import TunerConfig

@dataclass
class HyperbandTunerConfig(TunerConfig):
	reduction_factor: int = 3
	iterations: int = 100
	max_epochs: int = 10
