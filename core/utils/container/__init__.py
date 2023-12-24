from dependency_injector.providers import Configuration
from dataclasses import fields
from core.utils.config import Config

def to_dependency_injector_configuration(config: Config):
	configuration = Configuration()
	for field in fields(config):
			getattr(configuration, field.name).from_value(getattr(config, field.name))
	configuration.raw.from_value(config)
	return configuration