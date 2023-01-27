from pydantic import BaseSettings

class TrainerConfig(BaseSettings):
	epochs: int = 100
	steps_per_epoch: int = 20