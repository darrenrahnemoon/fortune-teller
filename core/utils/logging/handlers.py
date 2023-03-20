import os
import sys
from logging import FileHandler, StreamHandler
from .formatter import ColoredFormatter
from logging_json import JSONFormatter

from core.utils.time import now
from core.utils.environment import project_directory

class JSONFileHandler(FileHandler):
	def __init__(self) -> None:
		super().__init__(project_directory.joinpath(f"core/artifacts/logs/{now(os.getenv('TIMEZONE', 'UTC'))}.json"))
		self.formatter = JSONFormatter(
			fields = {
				'level' : 'levelname',
				'module' : 'name',
				'function' : 'funcName',
				'process' : 'process',
				'timestamp' : 'asctime',
			}
		)

class STDOUTHandler(StreamHandler):
	def __init__(self):
		super().__init__(sys.stdout)
		self.formatter = ColoredFormatter(
			colored_format = '[%(process)d][%(asctime)s][%(levelname)s][%(name)s][%(funcName)s]:\n',
			uncolored_format = '%(message)s\n'
		)