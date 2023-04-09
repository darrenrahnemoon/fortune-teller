import sys
import os
import dotenv
import tempfile
from pathlib import Path
from typing import Any, Literal

# Setup project directory
project_directory = Path(__file__).joinpath('../../../../').resolve()
os.chdir(str(project_directory))
sys.path.append(str(project_directory))

# Move pycache files to temp
sys.pycache_prefix = tempfile.gettempdir()

# Load environment variables
dotenv.load_dotenv('.env')

stage: Literal['development', 'production'] = 'development'

def set_variable_in_env_file(key: str, value: Any):
	dotenv.set_key('.env', key, value)

is_windows = sys.platform.startswith('win')
is_macos = 'darwin' in sys.platform 