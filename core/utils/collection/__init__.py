from typing import TypeVar, Iterable, Callable

T = TypeVar('T')

def ensure_list(potential_list: Iterable[T] or T) -> list[T]:
	if potential_list == None:
		return potential_list
	if type(potential_list) == list:
		return potential_list
	return [ potential_list ]

def is_any_of(iterable: Iterable[T], check: Callable[[T], bool]) -> bool:
	return next((True for item in iterable if check(item)), False)

def find(iterable: Iterable[T], check: Callable[[T], bool]) -> T:
	return next((item for item in iterable if check(item)), None)

def is_all_of(iterable: Iterable[T], check: Callable[[T], bool]) -> bool:
	for item in iterable:
		if not check(item):
			return False
	return True
