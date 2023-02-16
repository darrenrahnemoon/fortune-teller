if __name__ == '__main__':
	import sys
	from argparse import ArgumentParser

	import core.utils.environment
	import core.utils.logging
	from core.utils.module import import_module
	import core.utils.command.environment as environment_cli
	import core.utils.command.logging as logging_cli

	command = import_module(sys.argv[1])
	parser = ArgumentParser()

	environment_cli.add_to_arguments(parser)
	logging_cli.add_to_arguments(parser)

	if hasattr(command, 'config'):
		command.config(parser)
	
	args = parser.parse_args(sys.argv[2:]) # HACK: since python always starts from run.py ignore the first arg
	logging_cli.set_log_level_from_arguments(args)
	environment_cli.set_environment_from_arguments(args)
	command.handler(args)
