import pandas
import inspect
import termcolor
from dataclasses import is_dataclass, fields as get_fields
from types import NoneType
from typing import ClassVar, TypedDict, get_origin

from core.utils.collection import is_any_of

class PrettyReprColorConfig(TypedDict):
	init: str
	key: str
	value: str
	separator: str

def pretty_repr(
	target,
	indent = 0,
	indent_character = '  ',
	colored: PrettyReprColorConfig = False,
	fields = [],
	cache = [],
):
	# Args need one extra indentation
	args_indent_str = indent_character * (indent + 1)
	indent_str = indent_character * indent

	def pretty_repr_field(target):
		return pretty_repr(
			target,
			indent = indent + 1,
			indent_character = indent_character,
			colored = colored,
			cache = cache
		)

	def apply_color(value, name: str):
		if not colored:
			return value
		color = colored[name]
		return termcolor.colored(value, color)

	def repr_opening(value):
		value = apply_color(value, 'init')
		return value

	def repr_argument(*args, separator = ' = '):
		args = list(args)
		args[-1] = pretty_repr_field(args[-1])
		args[-1] = apply_color(args[-1], 'value')
		if len(args) > 1:
			args[0] = apply_color(args[0], 'key')
		separator = apply_color(separator, 'separator')
		return f'\n{args_indent_str}{separator.join(args)},'

	def repr_closing(value):
		value = apply_color(value, 'init')
		return f'\n{indent_str}{value}'

	# Check for circular reference
	if is_any_of(cache, lambda item: id(item) == id(target)):
		return '...'

	# Don't cache 'primitive' types
	if type(target) not in [ NoneType, int, str, bool, pandas.Timestamp ]:
		cache.append(target)

	if type(target) == list:
		result = repr_opening('[')
		for item in target:
			result += repr_argument(item, separator = '')
		result += repr_closing(']')
		return result

	if inspect.isclass(target):
		return repr(target)

	if type(target) == dict:
		result = repr_opening('{')
		for key, value in target.items():
			result += repr_argument(pretty_repr_field(key), value, separator = ' : ')
		result += repr_closing('}')
		return result

	if is_dataclass(target) and len(fields) == 0:
		result = repr_opening(f'{type(target).__name__}(')
		fields = [ 
			field.name
			for field in get_fields(target)
			if field.repr and not get_origin(field.type) == ClassVar
		]

	if len(fields):
		for field in fields:
			result += repr_argument(field, getattr(target, field))
		result += repr_closing(')')
		return result

	return repr(target)