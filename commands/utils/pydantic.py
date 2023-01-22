from pydantic import BaseSettings
from argparse import ArgumentParser, Namespace

from .cls import add_class_fields_as_arguments, setattr_from_args

def add_configuration_as_arguments(
	parser: ArgumentParser,
	cls: type[BaseSettings],
):
	add_class_fields_as_arguments(parser, cls, recursive = [ BaseSettings ])

def get_overridden_configuration_from_arguments(
	args: Namespace,
	cls: type[BaseSettings],
):
	config = cls()
	setattr_from_args(args, config, recursive = [ BaseSettings ])
	return config
