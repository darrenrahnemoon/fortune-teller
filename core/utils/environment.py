import sys
import os
import pathlib
import dotenv
import tempfile
from typing import Any, Literal

project_directory = pathlib.Path(__file__).joinpath('../../../').resolve()
os.chdir(str(project_directory))
sys.path.append(str(project_directory))

sys.pycache_prefix = tempfile.gettempdir()

dotenv.load_dotenv('.env')

stage: Literal['development', 'production'] = 'development'

@staticmethod
def set_variable_in_env_file(key: str, value: Any):
	dotenv.set_key('.env', key, value)
