import argparse
import subprocess
from shutil import rmtree

from apps.next_period_high_low.strategy import NextPeriodHighLowStrategy
from core.broker.simulation import SimulationBroker
from core.interval import Interval
from core.utils.command import Command

class TuneModelCommand(Command):
	def config(self):
		self.parser.add_argument('--tensorboard', action = argparse.BooleanOptionalAction)
		self.parser.add_argument('--clean', action = argparse.BooleanOptionalAction)

	def handler(self):
		broker = SimulationBroker()
		strategy = NextPeriodHighLowStrategy(
			alphavantage_broker = broker,
			metatrader_broker = broker,
			interval = Interval.Minute(1),
			backward_window_length = Interval.Day(1),
			forward_window_length = Interval.Minute(10),
		)
		strategy.service.dataset.cache()
		# if self.args.clean:
		# 	rmtree(strategy.service.keras_tuner_directory, ignore_errors = True)
		# 	rmtree(strategy.service.tensorboard_directory, ignore_errors = True)

		# tensorboard_process = None
		# if self.args.tensorboard:
		# 	tensorboard_process = subprocess.Popen([
		# 		'tensorboard',
		# 		'--logdir',
		# 		strategy.service.tensorboard_directory
		# 	],
		# 	stdout = subprocess.PIPE,
		# 	stderr = subprocess.PIPE
		# )

		# try:
		# 	strategy.service.tune_model()
		# finally:
		# 	if tensorboard_process:
		# 		tensorboard_process.terminate()