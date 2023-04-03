from pathlib import Path

from core.tensorflow.device.config import DeviceConfig
from core.tensorflow.dataset.config import DatasetConfig
from core.tensorflow.tuner.hyperband.config import HyperbandTunerConfig
from core.tensorflow.trainer.config import TrainerConfig
from core.tensorflow.tensorboard.config import TensorboardConfig
from core.utils.config import Config, dataclass, field
from .observation import ObservationConfig
from .action import ActionConfig

@dataclass
class NextPeriodHighLowStrategyConfig(Config):
	observation: ObservationConfig = field(default_factory = ObservationConfig)
	action: ActionConfig = field(default_factory = ActionConfig)

@dataclass
class NextPeriodHighLowConfig(Config):
	dataset: DatasetConfig = field(default_factory = DatasetConfig)
	device: DeviceConfig = field(default_factory = DeviceConfig)
	tensorboard: TensorboardConfig = field(default_factory = TensorboardConfig)
	trainer: TrainerConfig = field(default_factory = TrainerConfig)
	tuner: HyperbandTunerConfig = field(default_factory = HyperbandTunerConfig)
	strategy: NextPeriodHighLowStrategyConfig = field(default_factory = NextPeriodHighLowStrategyConfig)
	artifacts_directory: Path = Path('./apps/next_period_high_low/artifacts')