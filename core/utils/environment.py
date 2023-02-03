import sys
import os
import pathlib
import dotenv
import tempfile
from typing import Literal

project_directory = pathlib.Path(__file__).joinpath('../../../').resolve()
project_directory_str = str(project_directory)
os.chdir(project_directory_str)
sys.path.append(project_directory_str)

sys.pycache_prefix = tempfile.gettempdir()

dotenv.load_dotenv('.env')

class stage:
	value: Literal['training', 'tuning', 'production'] = None

	@staticmethod
	def set(value):
		stage.value = value

	@staticmethod
	def get():
		return stage.value

class env:
	@staticmethod
	def set(key: str, value):
		dotenv.set_key('.env', key, value)
