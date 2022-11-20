import sys
import lib.utils.environment
import lib.utils.logging

from lib.utils.command import Command

Command.run_from_path(sys.argv[1])