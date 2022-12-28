if __name__ == '__main__':
	import sys
	import core.utils.environment
	import core.utils.logging

	from core.utils.command import Command

	Command.run_from_path(sys.argv[1])