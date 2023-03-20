from dataclasses import dataclass
from argparse import BooleanOptionalAction
from dataclasses import fields
from caseconverter import kebabcase

from core.utils.collection import is_any_of
from core.utils.serializer import RepresentationSerializer

@dataclass
class ClassCommandSession:
	def add_class_fields_to_arguments(
		self,
		cls,
		select: list[str] = [],
		omit: list[str] = [],
		recursive: list = [],
		prefix: str = '',
		args = [],
		kwargs = {},
		group = None
	):
		group = group or self.parser
		for field in fields(cls):
			if field.name in omit:
				continue
			elif len(select) and field.name not in select:
				continue

			if is_any_of(recursive, lambda x: issubclass(field.type, x)):
				self.add_class_fields_to_arguments(
					cls = field.type,
					prefix = field.name,
					group = group,
				)
				continue

			option_string = '--'
			if prefix:
				option_string += f'{kebabcase(prefix)}-'
			option_string += kebabcase(field.name)

			# skip if option string has been previously defined
			if is_any_of(self.parser._actions, lambda action: option_string in action.option_strings):
				continue

			if field.type == bool:
				group.add_argument(
					option_string,
					*args,
					action = BooleanOptionalAction,
					**kwargs
				)
			else:
				group.add_argument(
					option_string,
					*args,
					type = RepresentationSerializer(field.type).deserialize,
					**kwargs
				)

	def set_instance_fields_from_arguments(
		self,
		instance,
		recursive: list = [],
		prefix = '',
	):
		for field in fields(type(instance)):
			if is_any_of(recursive, lambda x: issubclass(field.type, x)):
				self.set_instance_fields_from_arguments(
					instance = getattr(instance, field.name),
					prefix = field.name,
				)
				continue

			name = f'{prefix}_{field.name}' if prefix else field.name
			value = getattr(self.args, name, None)
			if value == None:
				continue

			setattr(instance, field.name, value)