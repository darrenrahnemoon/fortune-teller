from dataclasses import dataclass, field
from . import Config

from core.utils.cls.command import ClassCommandSession

@dataclass
class ConfigCommandSession(ClassCommandSession):
	config: Config = field(default_factory = Config)

	def setup(self):
		super().setup()
		self.add_config_fields_to_arguments(type(self.config))

	def run(self):
		super().run()
		self.set_config_fields_from_arguments(self.config)

	def add_config_fields_to_arguments(
		self,
		cls: type[Config],
	):
		group = self.parser.add_argument_group('config')
		self.add_class_fields_to_arguments(
			cls = cls,
			recursive = [ Config ],
			group = group
		)

	def set_config_fields_from_arguments(
		self,
		config: Config,
	):
		self.set_instance_fields_from_arguments(
			instance = config,
			recursive = [ Config ]
		)