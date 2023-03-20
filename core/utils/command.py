from dataclasses import dataclass

from argparse import ArgumentParser, Namespace
from core.utils.logging.command import LoggingCommandSession
from core.utils.environment.command import EnvironmentCommandSession

@dataclass
class _CommandSession:
	parser: ArgumentParser = None
	args: Namespace = None

	def setup(self):
		pass

	def run(self):
		pass

	@classmethod
	def build(cls, argv):
		session: 'CommandSession' = cls()
		session.parser = ArgumentParser()
		session.setup()
		session.args = session.parser.parse_args(argv)
		session.run()

@dataclass
class CommandSession(
	LoggingCommandSession,
	EnvironmentCommandSession,
	_CommandSession
):
	pass