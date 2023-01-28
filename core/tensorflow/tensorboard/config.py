from pydantic import BaseSettings

class TensorboardConfig(BaseSettings):
	enabled: bool = False
	port: str or int = 'default'
