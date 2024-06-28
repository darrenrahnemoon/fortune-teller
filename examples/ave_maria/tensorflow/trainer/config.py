from dataclasses import dataclass
from core.tensorflow.trainer.config import TrainerConfig

@dataclass
class AveMariaTrainerConfig(TrainerConfig):
	direction_loss_weight: float = 1
	high_low_loss_weight: float = 1