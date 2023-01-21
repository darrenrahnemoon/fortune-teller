if __name__ == '__main__':
	import sys
	from argparse import ArgumentParser

	import core.utils.environment
	import core.utils.logging
	from core.utils.module import import_module

	command = import_module(sys.argv[1])
	parser = ArgumentParser()
	if hasattr(command, 'config'):
		command.config(parser)

	args = parser.parse_args(sys.argv[2:]) # HACK: since python always starts from run.py ignore the first arg
	command.handler(args)
