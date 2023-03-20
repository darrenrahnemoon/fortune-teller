from dependency_injector.containers import DynamicContainer
from dataclasses import dataclass, fields
from core.utils.config.command import ConfigCommandSession

@dataclass
class ContainerCommandSession(ConfigCommandSession):
	container: DynamicContainer = None

	def run(self):
		super().run()
		container_cls = next(field.type for field in fields(type(self)) if field.name == 'container')
		self.container = container_cls(config = self.config)