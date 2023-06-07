from dataclasses import dataclass
from core.tensorflow.trainer.config import TrainerConfig

@dataclass
class NextPeriodHighLowTrainerConfig(TrainerConfig):
	numerical_loss_scale: int = 1
	direction_loss_scale: int = 1