from typing import TypeVar, Iterable, Callable

V = TypeVar('V')

def ensure_list(potential_list: list[V] or V) -> list[V]:
	if potential_list == None:
		return potential_list
	return potential_list if type(potential_list) == list else [ potential_list ]

def is_any_of(iterable: Iterable, check: Callable) -> bool:
	return next((True for item in iterable if check(item)), False)

def is_all_of(iterable: Iterable, check: Callable) -> bool:
	for item in iterable:
		if not check(item):
			return False
	return True
