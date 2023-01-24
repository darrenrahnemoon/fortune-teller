from pydantic import BaseSettings

class TensorboardConfig(BaseSettings):
	enabled: bool = False
