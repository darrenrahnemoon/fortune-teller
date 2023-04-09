from dataclasses import dataclass
from core.utils.command import CommandSession
from core.utils.config.command import ConfigCommandSession
from core.utils.test.config import TestManagerConfig
from core.utils.test import test

@dataclass
class TestCommandSession(
	ConfigCommandSession,
	CommandSession
):
	config: TestManagerConfig = None

	def setup(self):
		super().setup()
		self.parser.add_argument('--patterns', nargs = '*', default = [ '**/tests/**/*.py' ])
		self.parser.add_argument('--filter', '-f', type = str, default = '')

	def run(self):
		super().run()
		test.config = self.config
		test.root.config = self.config.test_group # HACK: need a better way to automatically update root config based on manager config
		test.load_files(self.args.patterns)
		test.run(filter_name = self.args.filter)