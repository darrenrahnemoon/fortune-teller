from dataclasses import dataclass
import core.utils.environment as environment

@dataclass
class EnvironmentCommandSessionMixin:
	def setup(self):
		super().setup()
		group = self.parser.add_argument_group('environment')
		group.add_argument('--stage', choices = [ 'development', 'production' ], default = 'development')

	def run(self):
		super().run()
		environment.stage = self.args.stage or environment.stage
