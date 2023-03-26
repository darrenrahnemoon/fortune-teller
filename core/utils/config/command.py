from dataclasses import dataclass, fields
from . import Config

from core.utils.cls.command import ClassCommandSession

@dataclass
class ConfigCommandSession(ClassCommandSession):
	config: Config = None

	@property
	def config_cls(self):
		return next(field.type for field in fields(type(self)) if field.name == 'config')

	def setup(self):
		super().setup()
		self.add_config_fields_to_arguments(self.config_cls)

	def run(self):
		super().run()
		self.config = self.config_cls()
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