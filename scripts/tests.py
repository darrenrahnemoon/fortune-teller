from lib.utils.command import Command
from lib.utils.test import TestManager

class TestsCommand(Command):
	def config(self):
		self.parser.add_argument('--patterns', nargs='+', default=[ 'tests/**/*.py' ])
		self.parser.add_argument('--filter', '-f', type=str, default='')

	def handler(self):
		TestManager.load_from_files(self.args.patterns)
		TestManager.run_all(self.args.filter)