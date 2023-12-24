from pathlib import Path

from core.tensorflow.device.config import DeviceConfig
from core.tensorflow.dataset.config import DatasetConfig
from core.tensorflow.tuner.random.config import RandomSearchTunerConfig
from core.tensorflow.tensorboard.config import TensorboardConfig
from core.utils.config import Config, dataclass, field

from apps.pelosi_predictor.trainer.config import PelosiPredictorTrainerConfig
from .observation import ObservationConfig
from .action import ActionConfig

@dataclass
class PelosiPredictorStrategyConfig(Config):
	observation: ObservationConfig = field(default_factory = ObservationConfig)
	action: ActionConfig = field(default_factory = ActionConfig)

@dataclass
class PelosiPredictorConfig(Config):
	dataset: DatasetConfig = field(default_factory = DatasetConfig)
	device: DeviceConfig = field(default_factory = DeviceConfig)
	tensorboard: TensorboardConfig = field(default_factory = TensorboardConfig)
	trainer: PelosiPredictorTrainerConfig = field(default_factory = PelosiPredictorTrainerConfig)
	tuner: RandomSearchTunerConfig = field(default_factory = RandomSearchTunerConfig)
	strategy: PelosiPredictorStrategyConfig = field(default_factory = PelosiPredictorStrategyConfig)
	artifacts_directory: Path = Path('./apps/pelosi_predictor/artifacts')