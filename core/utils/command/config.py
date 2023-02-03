from argparse import ArgumentParser, Namespace
from typing import TypeVar
from core.utils.config import Config
import core.utils.command.cls

def add_fields_to_args(
	parser: ArgumentParser,
	cls: type[Config],
):
	core.utils.command.cls.add_fields_to_args(
		parser = parser,
		cls = cls,
		recursive = [ Config ]
	)

T = TypeVar('T')
def set_fields_from_args(
	args: Namespace,
	cls: type[T],
) -> T:
	config = cls()
	core.utils.command.cls.set_fields_from_args(
		args = args,
		instance = config,
		recursive = [ Config ]
	)
	return config
