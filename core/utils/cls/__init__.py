from itertools import product
from typing import Any, Iterable, TypeVar

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

T = TypeVar('T')
def product_dict(combinations: dict[list[T]]) -> list[dict[str, T]]:
	return [
		dict(
			zip(combinations.keys(), combination)
		)
		for combination in product(*combinations.values())
	]
