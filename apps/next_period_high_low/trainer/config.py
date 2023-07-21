from dataclasses import dataclass
from core.tensorflow.trainer.config import TrainerConfig

@dataclass
class NextPeriodHighLowTrainerConfig(TrainerConfig):
	high_low_loss_weight: int = 1
	direction_loss_weight: int = 1