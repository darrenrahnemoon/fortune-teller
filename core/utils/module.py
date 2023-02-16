import sys
import glob
import importlib.util
import importlib

def import_module(path: str, to_path: str = None):
	"""Imports a module based on a directory/module style path

	Args:
		path (str): Can be either 'foo.bar.xo' or 'foo/bar/xo.py'

	Returns:
		module: the imported module
	"""
	directory_separator = '/' if '/' in path else '\\'
	module_name = '.'.join(path.split(directory_separator))
	if '.py' in path:
		module_name = module_name.replace('.py', '')

	if module_name in sys.modules:
		imported_module = sys.modules[module_name]
	else:
		imported_module = importlib.import_module(module_name)

	sys.modules[to_path or module_name] = imported_module

	return imported_module

def import_modules(patterns: list[str]):
	"""Imports a group of modules defined by a list of glob patterns

	Args:
		patterns (list[str]): list of glob patterns
	"""
	for pattern in patterns:
		for path in glob.glob(pattern, recursive=True):
			import_module(path)
