from argparse import ArgumentParser, Namespace
from core.utils.config import Config

from .cls import add_class_fields_as_arguments, setattr_from_args

def add_configuration_as_arguments(
	parser: ArgumentParser,
	cls: type[Config],
):
	add_class_fields_as_arguments(parser, cls, recursive = [ Config ])

def get_overridden_configuration_from_arguments(
	args: Namespace,
	cls: type[Config],
):
	config = cls()
	setattr_from_args(args, config, recursive = [ Config ])
	return config
