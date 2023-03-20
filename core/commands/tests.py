from dataclasses import dataclass
from core.utils.command import CommandSession
from core.utils.test import TestManager

@dataclass
class TestCommandSession(CommandSession):
	def setup(self):
		super().setup()
		self.parser.add_argument('--patterns', nargs = '*', default = [ '**/tests/**/*.py' ])
		self.parser.add_argument('--filter', '-f', type = str, default = '')

	def run(self):
		super().run()
		TestManager.load_from_files(self.args.patterns)
		TestManager.run_all(self.args.filter)