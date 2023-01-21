from argparse import ArgumentParser, BooleanOptionalAction, Namespace
from subprocess import Popen, PIPE
import atexit

def add_tensorboard_argument(parser: ArgumentParser):
	parser.add_argument('--tensorboard', action = BooleanOptionalAction)

def ensure_tensorboard_running(args: Namespace, directory: str):
	tensorboard_process = None
	if args.tensorboard:
		tensorboard_process = Popen(
			[
				'tensorboard',
				'--logdir',
				directory
			],
			stdout = PIPE,
			stderr = PIPE
		)
		atexit.register(tensorboard_process.terminate)
