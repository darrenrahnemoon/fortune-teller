from dataclasses import dataclass
from pathlib import Path
from keras.callbacks import TensorBoard

from core.tensorflow.tensorboard.config import TensorboardConfig
from core.tensorflow.artifact.service import ArtifactService

@dataclass
class TensorboardService(ArtifactService):
	config: TensorboardConfig = None

	@property
	def callbacks(self):
		if self.enabled:
			return [ TensorBoard(log_dir = self.directory) ]
		return []

	@property
	def directory(self) -> Path:
		return self.artifacts_directory.joinpath('tensorboard')