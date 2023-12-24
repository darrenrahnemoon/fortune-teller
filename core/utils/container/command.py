from dependency_injector.containers import DeclarativeContainer

from dataclasses import dataclass, fields
from core.utils.config.command import ConfigCommandSessionMixin
from core.utils.container import to_dependency_injector_configuration

@dataclass
class ContainerCommandSessionMixin(ConfigCommandSessionMixin):
	container: DeclarativeContainer = None

	@property
	def container_cls(self):
		return next(field.type for field in fields(type(self)) if field.name == 'container')

	def run(self):
		super().run()
		self.container = self.container_cls(
			config = to_dependency_injector_configuration(self.config)
		)