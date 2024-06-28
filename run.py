def main():
	import inspect
	import sys
	import core.utils.environment # To setup pycache, .env, etc.

	from core.utils.command import CommandSession
	from core.utils.module import import_module

	command_module = import_module(sys.argv[1])

	for command in command_module.__dict__.values():
		if inspect.isclass(command) \
			and issubclass(command, CommandSession) \
			and command != CommandSession:

			command.build(sys.argv[2:]) # HACK: since python always starts from run.py ignore the first arg
			break

if __name__ == '__main__':
	main()