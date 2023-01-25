from argparse import ArgumentParser, BooleanOptionalAction, Namespace
from dataclasses import is_dataclass
from caseconverter import kebabcase
from pydantic import BaseModel

from core.utils.collection import is_any_of
from core.utils.serializer import RepresentationSerializer

def get_fields(cls):
	# Check for pydantic classes
	if issubclass(cls, BaseModel):
		return { field.name: field.type_ for field in getattr(cls, '__fields__').values() }

	# Check for dataclasses
	if is_dataclass(cls):
		return { field.name: field.type for field in getattr(cls, '__dataclass_fields__').values() }
	
	raise Exception(f'Unable to infer field type hints for {cls}')

def add_class_fields_as_arguments(
	parser: ArgumentParser,
	cls,
	select: list[str] = [],
	omit: list[str] = [],
	recursive: list = [],
	prefix: str = '',
	args = [],
	kwargs = {},
):
	fields = get_fields(cls)

	for field_name, field_type in fields.items():
		if field_name in omit:
			continue
		elif len(select) and field_name not in select:
			continue

		if is_any_of(recursive, lambda x: issubclass(field_type, x)):
			add_class_fields_as_arguments(
				cls = field_type,
				parser = parser,
				prefix = field_name
			)
			continue

		option_string = '--'
		if prefix:
			option_string += f'{kebabcase(prefix)}-'
		option_string += kebabcase(field_name)

		# skip if option string has been previously defined
		if is_any_of(parser._actions, lambda action: option_string in action.option_strings):
			continue

		if field_type == bool:
			parser.add_argument(
				option_string,
				*args,
				action = BooleanOptionalAction,
				**kwargs
			)
		else:
			parser.add_argument(
				option_string,
				*args,
				type = RepresentationSerializer(field_type).deserialize,
				**kwargs
			)

def setattr_from_args(
	args: Namespace,
	instance,
	recursive: list = [],
	prefix = '',
):
	fields = get_fields(type(instance))
	for field_name, field_type in fields.items():
		if is_any_of(recursive, lambda x: issubclass(field_type, x)):
			setattr_from_args(
				instance = getattr(instance, field_name),
				args = args,
				prefix = field_name,
			)
			continue

		name = f'{prefix}_{field_name}' if prefix else field_name
		value = getattr(args, name, None)
		if value == None:
			continue

		setattr(instance, field_name, value)