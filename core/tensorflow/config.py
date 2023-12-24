from pathlib import Path
from dataclasses import field, dataclass
from core.utils.config import Config

from core.tensorflow.device.config import DeviceConfig
from core.tensorflow.dataset.config import DatasetConfig
from core.tensorflow.tuner.random.config import RandomSearchTunerConfig
from core.tensorflow.tensorboard.config import TensorboardConfig
from core.tensorflow.trainer.config import TrainerConfig

@dataclass
class TensorflowConfig(Config):
	dataset: DatasetConfig = field(default_factory = DatasetConfig)
	device: DeviceConfig = field(default_factory = DeviceConfig)
	tensorboard: TensorboardConfig = field(default_factory = TensorboardConfig)
	trainer: TrainerConfig = field(default_factory = TrainerConfig)
	tuner: RandomSearchTunerConfig = field(default_factory = RandomSearchTunerConfig)
	artifacts_directory: Path = Path('./core/artifacts/tensorflow')