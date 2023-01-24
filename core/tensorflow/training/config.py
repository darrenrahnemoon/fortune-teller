from pydantic import BaseSettings

class TrainingConfig(BaseSettings):
	epochs: int = 100
	steps_per_epoch: int = 100