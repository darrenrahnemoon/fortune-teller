import pandas
import termcolor
from dataclasses import is_dataclass
from itertools import product
from types import NoneType
from typing import Any, Iterable, ClassVar, TypedDict, get_origin

from core.utils.collection import is_any_of

def ensureattr(obj: Any, name: str, default: Any):
	"""Check if an attribute exists on object and if not set it to default

	Args:
		obj (Any): object
		name (str): field name
		default (Any): default value in case the field doesn't exist

	Returns:
		Any: the value that is finally stored in the field of the object
	"""
	try:
		return getattr(obj, name)
	except:
		setattr(obj, name, default)
		return default

def pickattrs(obj, names: Iterable[str]) -> dict:
	return {
		attr: getattr(obj, attr)
		for attr in names
	}

def product_dict(combinations: dict[list]):
	return (
		dict(
			zip(combinations.keys(), combination)
		)
		for combination in product(*combinations.values())
	)

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

	if type(target) == dict:
		result = repr_opening('{')
		for key, value in target.items():
			result += repr_argument(pretty_repr_field(key), value, separator = ' : ')
		result += repr_closing('}')
		return result

	if is_dataclass(target):
		result = repr_opening(f'{type(target).__name__}(')
		fields = getattr(target, '__dataclass_fields__')
		for field in fields.values():
			if not field.repr:
				continue
			if get_origin(field.type) is ClassVar:
				continue
			result += repr_argument(field.name, getattr(target, field.name))
		result += repr_closing(')')
		return result

	return repr(target)