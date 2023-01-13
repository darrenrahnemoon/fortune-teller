from abc import abstractmethod
import argparse
import inspect
import sys
import caseconverter

from core.utils.module import import_module
from .serializers import *

class Command:
	def __init__(self) -> None:
		self.parser = argparse.ArgumentParser()
		self.config()

	@staticmethod
	def register(command_class):
		command_class.__maincommand__ = True
		return command_class

	def run(self):
		self.args = self.parser.parse_args(sys.argv[2:]) # HACK: since python always starts from run.py ignore the first arg
		self.handler()

	def config(self):
		"""Configure the arguments and flags that this `Command` should handle using `self.parser`"""
		pass

	@abstractmethod
	def handler(self):
		"""Runs when the `Command` is being executed. Can access the arguments from `self.args`"""
		pass

	@staticmethod
	def run_from_path(path: str):
		"""Run the first occurrence of a `Command` subclass specified in the passed path

		Args:
			path (str): path of the file containing the `Command` subclass
		"""
		for possible_command in import_module(path).__dict__.values():
			if inspect.isclass(possible_command)\
				and issubclass(possible_command, Command)\
				and getattr(possible_command, '__maincommand__', False):
				possible_command().run()

class KeyValuePairsAction(argparse.Action):
	"""Allows an argument flag to be a sequence of space delimited key-value pairs
		Example:
			Given: --foo key1=bar key2=oxo
			Expect: args.foo = dict(
				key1='bar',
				key2='xox'
			)
	"""
	def __call__(self, parser, namespace, values, option_string = None):
		setattr(namespace, self.dest, dict())
		for value in values:
			key, value = value.split('=')
			getattr(namespace, self.dest)[key.strip()] = value.strip()

def map_dict_to_argument(dictionary: dict[str]):
	"""Alters the argument so that in the the key of the dictionary is accepted as command values and in runtime the mapped value of the dictionary is returned as a argument in the args namespace of the parse command

	Args:
		dictionary (dict[str]): mapping of command line string choices to runtime values

	Returns:
		dict: a dictionary that needs to be spread in the kwargs of the Argument. It will overwrite 'choices' and 'action'
	"""
	arguments = dict()
	arguments['choices'] = list(dictionary.keys())

	# Using an `action` instead of a `type` so that choices shown in --help are dictionary keys not values
	# When `type` is present in `add_argument` args it expects the `choices` to be the transformed values which might not have `__repr__` or `__str__`
	class MapDictionaryValue(argparse.Action):
		def __call__(self, parser, namespace, keys, option_string = None):
			if type(keys) == list:
				setattr(namespace, self.dest, [ dictionary[key] for key in keys ])
			else:
				setattr(namespace, self.dest, dictionary[keys])
	arguments['action'] = MapDictionaryValue

	return arguments
