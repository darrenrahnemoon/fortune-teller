from dataclasses import dataclass
from pathlib import Path
from shutil import rmtree

@dataclass
class ArtifactService:
	artifacts_directory: Path = None

	@property
	def directory(self):
		pass

	def clean(self):
		return rmtree(self.directory, ignore_errors = True)