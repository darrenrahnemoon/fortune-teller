from dataclasses import field, dataclass

from core.tensorflow.config import TensorflowConfig
from apps.ave_maria.tensorflow.trainer.config import AveMariaTrainerConfig
from apps.ave_maria.tensorflow.tuner.config import AveMariaTunerConfig

@dataclass
class AveMariaTensorflowConfig(TensorflowConfig):
	trainer: AveMariaTrainerConfig = field(default_factory = AveMariaTrainerConfig)
	tuner: AveMariaTunerConfig = field(default_factory = AveMariaTunerConfig)
