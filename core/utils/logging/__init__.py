import os
import sys
import logging

from core.utils.logging.formatter import ColoredFormatter

stdout_stream = logging.StreamHandler(sys.stdout)
stdout_stream.formatter = ColoredFormatter()
logging.basicConfig(
	level=os.getenv("LOG_LEVEL", "DEBUG").upper(),
	handlers=[stdout_stream]
)
