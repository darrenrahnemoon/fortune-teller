import sys
import glob
import importlib.util
import importlib

def import_module(path: str):
	"""Imports a module based on a directory/module style path

	Args:
		path (str): Can be either 'foo.bar.xo' or 'foo/bar/xo.py'

	Returns:
		module: the imported module
	"""
	module_name = '.'.join(path.split('/'))
	if '.py' in path:
		module_name = module_name.replace('.py', '')
		spec = importlib.util.spec_from_file_location(module_name, path)
	else:
		spec = importlib.util.find_spec(module_name)
	if module_name in sys.modules:
		return sys.modules[module_name]
	imported_module = importlib.util.module_from_spec(spec)
	sys.modules[module_name] = imported_module
	return spec.loader.load_module(module_name)

def import_modules(patterns: list[str]):
	"""Imports a group of modules defined by a list of glob patterns

	Args:
		patterns (list[str]): list of glob patterns
	"""
	for pattern in patterns:
		for path in glob.glob(pattern, recursive=True):
			import_module(path)
