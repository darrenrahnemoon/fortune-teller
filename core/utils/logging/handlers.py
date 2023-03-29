import os
import sys
import glob
from pathlib import Path
from logging import FileHandler, StreamHandler
from .formatter import ColoredFormatter
from logging_json import JSONFormatter

from core.utils.time import now

class JSONFileHandler(FileHandler):
	def __init__(self) -> None:
		timestamp = now(os.getenv('TIMEZONE', 'UTC'))
		timestamp = timestamp.strftime('%Y-%m-%d-%H-%M-%S-%Z')
		self.json_log_path = Path(f"core/artifacts/logs/{timestamp}.json").resolve()
		super().__init__(self.json_log_path)
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