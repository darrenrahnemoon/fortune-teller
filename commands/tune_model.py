from core.utils.command import Command
from apps.next_period_high_low import tune_model

class TestsCommand(Command):
	def handler(self):
		tune_model()