from dataclasses import dataclass
from pathlib import Path
import tensorflow
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

			if self.config.debugger_enabled:
				tensorflow.debugging.experimental.enable_dump_debug_info(
					str(directory),
					tensor_debug_mode="FULL_HEALTH",
					circular_buffer_size=-1
				)

			return [
				TensorBoard(
					log_dir = directory,
					histogram_freq = self.config.histogram_frequency,
					write_images = self.config.write_images,
					write_steps_per_second = self.config.write_steps_per_second,
				)
			]
		return []

	@property
	def directory(self) -> Path:
		return self.artifacts_directory.joinpath('tensorboard')