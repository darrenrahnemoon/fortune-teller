from pathlib import Path

from core.tensorflow.device.config import DeviceConfig
from core.tensorflow.dataset.config import DatasetConfig
from core.tensorflow.tuner.random.config import RandomSearchTunerConfig
from core.tensorflow.tensorboard.config import TensorboardConfig
from core.utils.config import Config, dataclass, field

from apps.magic_crystal.trainer.config import MagicCrystalTrainerConfig
from .observation import ObservationConfig
from .action import ActionConfig

@dataclass
class MagicCrystalStrategyConfig(Config):
	observation: ObservationConfig = field(default_factory = ObservationConfig)
	action: ActionConfig = field(default_factory = ActionConfig)

@dataclass
class MagicCrystalConfig(Config):
	dataset: DatasetConfig = field(default_factory = DatasetConfig)
	device: DeviceConfig = field(default_factory = DeviceConfig)
	tensorboard: TensorboardConfig = field(default_factory = TensorboardConfig)
	trainer: MagicCrystalTrainerConfig = field(default_factory = MagicCrystalTrainerConfig)
	tuner: RandomSearchTunerConfig = field(default_factory = RandomSearchTunerConfig)
	strategy: MagicCrystalStrategyConfig = field(default_factory = MagicCrystalStrategyConfig)
	artifacts_directory: Path = Path('./apps/magic_crystal/artifacts')