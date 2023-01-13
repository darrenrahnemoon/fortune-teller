from core.utils.command import Command
from core.utils.test import TestManager

@Command.register
class TestsCommand(Command):
	def config(self):
		self.parser.add_argument('--patterns', nargs='+', default=[ 'tests/**/*.py' ])
		self.parser.add_argument('--filter', '-f', type=str, default='')

	def handler(self):
		TestManager.load_from_files(self.args.patterns)
		TestManager.run_all(self.args.filter)