from pydantic import BaseSettings

class HyperbandTunerConfig(BaseSettings):
	max_epochs: int = 10
	reduction_factor: int = 3
	iterations: int = 100
