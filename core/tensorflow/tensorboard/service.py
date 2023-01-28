import atexit
from dataclasses import dataclass
from pathlib import Path
from subprocess import Popen, PIPE
from keras.callbacks import TensorBoard

from core.tensorflow.tensorboard.config import TensorboardConfig
from core.tensorflow.artifact.service import ArtifactService

@dataclass
class TensorboardService(ArtifactService):
	config: TensorboardConfig = None

	@property
	def callbacks(self):
		if self.config.enabled:
			return [ TensorBoard(log_dir = self.directory) ]
		return []

	def ensure_running(self):
		if not self.config.enabled:
			return

		tensorboard_process = Popen(
			[
				'tensorboard',
				'--logdir',
				self.directory,
				'--port',
				self.config.port
			],
			stdout = PIPE,
			stderr = PIPE
		)
		atexit.register(tensorboard_process.terminate)

	@property
	def directory(self) -> Path:
		return self.artifacts_directory.joinpath('tensorboard')