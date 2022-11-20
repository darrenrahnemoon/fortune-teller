import typing

V = typing.TypeVar('V')

def ensure_list(potential_list: list[V] or V) -> list[V]:
	if potential_list == None:
		return potential_list
	return potential_list if type(potential_list) == list else [ potential_list ]
