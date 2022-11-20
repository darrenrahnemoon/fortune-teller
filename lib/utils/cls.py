import functools

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

class cachedclassproperty(object):
	"""Converts the method to a class getter that is cached after the first call"""
	def __init__(self, func):
		self.func = functools.cache(func)
	def __get__(self, obj, owner):
		return self.func(owner)

class hybridmethod(classmethod):
	"""Converts the method to a method who's first argument is the class or the instance depending on how it's been called"""
	def __get__(self, instance, type_):
		descriptor_get = super().__get__ if instance is None else self.__func__.__get__
		return descriptor_get(instance, type_)