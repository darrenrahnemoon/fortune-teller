from collections import defaultdict

################################################################################
#
#   NestedDict.py
#
#   Copyright (c) 2009, 2015 Leo Goodstadt
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#   THE SOFTWARE.
#
#################################################################################

def iterate_nested_dictionary(dictionary: dict):
	keystr = "keys"
	for key in dictionary.keys():
		value = dictionary[key]
		if hasattr(value, keystr):
			for keykey, value in iterate_nested_dictionary(value):
				yield (key,) + keykey, value
		else:
			yield (key,), value

class RecursiveDict(defaultdict):
	def items_flattened(self):
		for key, value in iterate_nested_dictionary(self):
			yield key, value

	def keys_flattened(self):
		for key, _ in iterate_nested_dictionary(self):
			yield key

	def values_flattened(self):
		for _, value in iterate_nested_dictionary(self):
			yield value

	def to_tupled_dict(self):
		return dict(iterate_nested_dictionary(self))

	def to_dict(self, input_dict = None):
		"""Convert the nested dictionary to a nested series of standard ``dict`` objects."""
		#
		# Calls itself recursively to unwind the dictionary.
		# Use to_dict() to start at the top level of nesting
		plain_dict = dict()
		if input_dict is None:
			input_dict = self
		for key in input_dict.keys():
			value = input_dict[key]
			if isinstance(value, RecursiveDict):
				# print "recurse", value
				plain_dict[key] = self.to_dict(value)
			else:
				# print "plain", value
				plain_dict[key] = value
		return plain_dict

class AnyType(object):
	pass


def create_nested_levels(level, nested_type):
	"""Helper function to create a specified degree of nested dictionaries."""
	if level > 2:
		return lambda: RecursiveDict(create_nested_levels(level - 1, nested_type))
	if level == 2:
		if isinstance(nested_type, AnyType):
			return lambda: RecursiveDict()
		else:
			return lambda: RecursiveDict(create_nested_levels(level - 1, nested_type))
	return nested_type

def get_nested_dict_from_dict(dictionary, nested_dictionary):
	"""Helper to build NestedDict from a dict."""
	for key, value in dictionary.items():
		if isinstance(value, (dict,)):
			nested_dictionary[key] = get_nested_dict_from_dict(value, NestedDict())
		else:
			nested_dictionary[key] = value
	return nested_dictionary

def update_recursively(nested_dictionary, other):
	for key, value in other.items():
		if isinstance(value, (dict,)):

			# recursive update if my item is NestedDict
			if isinstance(nested_dictionary[key], (RecursiveDict,)):
				update_recursively(nested_dictionary[key], other[key])

			# update if my item is dict
			elif isinstance(nested_dictionary[key], (dict,)):
				nested_dictionary[key].update(other[key])

			# overwrite
			else:
				nested_dictionary[key] = value
		# other not dict: overwrite
		else:
			nested_dictionary[key] = value
	return nested_dictionary

class NestedDict(RecursiveDict):
	def __init__(self, *param, **kwargs):
		if not len(param):
			self.factory = NestedDict
			defaultdict.__init__(self, self.factory)
			return

		if len(param) == 1:
			if isinstance(param[0], int):
				self.factory = create_nested_levels(param[0], AnyType())
				defaultdict.__init__(self, self.factory)
				return
			if isinstance(param[0], dict):
				self.factory = NestedDict
				defaultdict.__init__(self, self.factory)
				get_nested_dict_from_dict(param[0], self)
				return

		if len(param) == 2:
			if isinstance(param[0], int):
				self.factory = create_nested_levels(*param)
				defaultdict.__init__(self, self.factory)
				return

	def update(self, other):
		"""Update recursively."""
		update_recursively(self, other)

	@classmethod
	def from_tupled_dict(cls, dictionary: dict):
		instance = cls()
		for tuple_key, final_value in dictionary.items():
			value = instance
			for key in tuple_key[:-1]:
				value = value[key]
			value[tuple_key[-1]] = final_value
		return instance