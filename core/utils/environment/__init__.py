import sys
import os
import dotenv
import tempfile
from pathlib import Path
from typing import Any, Literal
from core.utils.module import import_module

project_directory = Path(__file__).joinpath('../../../../').resolve()
os.chdir(str(project_directory))
sys.path.append(str(project_directory))

sys.pycache_prefix = tempfile.gettempdir()

dotenv.load_dotenv('.env')

stage: Literal['development', 'production'] = 'development'

@staticmethod
def set_variable_in_env_file(key: str, value: Any):
	dotenv.set_key('.env', key, value)

is_windows = sys.platform.startswith('win')
is_macos = 'darwin' in sys.platform 

# HACK for MetaTraderRepository
# Intentionally imported this way so that importing this package on MacOS and Linux doesn't bork about MetaTrader5 which is only available on Windows
if not is_windows:
	import_module('core.utils.environment.MetaTrader5', to_path = 'MetaTrader5')