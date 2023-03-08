from dataclasses import dataclass
from pathlib import Path
from keras.callbacks import TensorBoard
from shutil import rmtree

from core.tensorflow.tensorboard.config import TensorboardConfig
from core.tensorflow.artifact.service import ArtifactService

@dataclass
class TensorboardService(ArtifactService):
	config: TensorboardConfig = None

	def get_callbacks(self, *args, scope = '', **kwargs):
		if self.config.enabled:
			directory = self.directory.joinpath(scope)
			if self.config.overwrite:
				rmtree(directory, ignore_errors = True)

			return [
				TensorBoard(log_dir = directory)
			]
		return []

	@property
	def directory(self) -> Path:
		return self.artifacts_directory.joinpath('tensorboard')