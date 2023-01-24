from pydantic import BaseSettings

class DeviceConfig(BaseSettings):
	use: str = 'CPU'
