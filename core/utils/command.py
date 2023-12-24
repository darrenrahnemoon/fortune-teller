from dataclasses import dataclass

from argparse import ArgumentParser, Namespace
from core.utils.logging.command import LoggingCommandSessionMixin
from core.utils.environment.command import EnvironmentCommandSessionMixin

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
	LoggingCommandSessionMixin,
	EnvironmentCommandSessionMixin,
	_CommandSession
):
	pass