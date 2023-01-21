import sys
import os
import pathlib
import dotenv
import tempfile

project_directory = pathlib.Path(__file__).joinpath('../../../').resolve()
project_directory_str = str(project_directory)
os.chdir(project_directory_str)
sys.path.append(project_directory_str)

sys.pycache_prefix = tempfile.gettempdir()

dotenv.load_dotenv('.env')

def set_env(key: str, value):
	dotenv.set_key('.env', key, value)