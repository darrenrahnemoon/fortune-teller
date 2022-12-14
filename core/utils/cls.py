from itertools import product
from typing import Generator

def ensureattr(__obj, __name, __default):
	"""Check if an attribute exists on object and if not set it to default

	Args:
		__obj (Any): object
		__name (str): field name
		__default (Any): default value in case the field doesn't exist

	Returns:
		Any: the value that is finally stored in the field of the object
	"""
	try:
		return getattr(__obj, __name)
	except:
		setattr(__obj, __name, __default)
		return __default

def product_dict(combinations: dict[list]) -> Generator[dict]:
	return (
		dict(
			zip(combinations.keys(), combination)
		)
		for combination in product(*combinations.values())
	)
