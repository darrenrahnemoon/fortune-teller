import os
import time
import traceback
import termcolor
import humanize

from core.utils.module import import_modules

class TestManager:
	settings = {
		'group_symbol' : os.getenv('TEST_GROUP_SYMBOL', '-'),
		'group_color' : os.getenv('TEST_GROUP_COLOR', 'magenta'),
		'case_symbol' : os.getenv('TEST_CASE_SYMBOL', '>'),
		'case_color' : os.getenv('TEST_CASE_COLOR', 'cyan'),
		'info_color' : os.getenv('TEST_INFO_COLOR', 'white'),
		'success_color' : os.getenv('TEST_ERROR_COLOR', 'green'),
		'error_color' : os.getenv('TEST_ERROR_COLOR', 'red'),
		'indentation' : os.getenv('TEST_INDENTATION', '\t'),
	}

	tests = dict()
	current_group = tests
	stats = {
		"success" : 0,
		"error" : 0,
	}

	@staticmethod
	def load_from_files(patterns: list[str]):
		import_modules(patterns)

	@classmethod
	def run_all(self, filter_message=''):
		self.stats = {
			"success" : 0,
			"error" : 0
		}
		self.run_tests(filter_message=filter_message)
		print(termcolor.colored('\n\nResults:', attrs=['bold']))
		print(termcolor.colored(f"Success: {self.stats['success']}", self.settings['success_color']))
		print(termcolor.colored(f"Error: {self.stats['error']}", self.settings['error_color']))

	@classmethod
	def run_tests(self, tests: dict = None, indent = 0, filter_message=''):
		tests = tests or self.tests
		indentation = self.settings['indentation'] * indent
		for message in tests:
			test = tests[message]
			filter_includes_message = filter_message.lower() in message.lower()
			if (type(test) == dict):
				print(termcolor.colored(f"\n{indentation}{self.settings['group_symbol']} {message}", self.settings['group_color']))
				self.run_tests(test, indent=indent + 1, filter_message='' if filter_includes_message else filter_message)
			else:
				if filter_includes_message:
					formatted_message = f"{indentation}{self.settings['case_symbol']} {message}:"
					print(termcolor.colored(formatted_message, self.settings['case_color']), end='\r')
					start_time = time.time()
					try:
						test()
						self.stats['success'] += 1
						print(
							termcolor.colored(formatted_message, self.settings['case_color']),
							termcolor.colored(f" Took {humanize.precisedelta(time.time() - start_time, minimum_unit = 'microseconds')}", self.settings['info_color'])
						)
					except Exception:
						self.stats['error'] += 1
						print(termcolor.colored(formatted_message, self.settings['error_color'])) 
						print(traceback.format_exc())

def describe(message: str):
	old_group = TestManager.current_group
	old_group[message] = TestManager.current_group = old_group[message] if message in old_group else dict()
	def decorator(func):
		func()
		TestManager.current_group = old_group
		return func
	return decorator

def it(message: str, skip=False, *args, **kwargs):
	def decorator(func):
		if not skip:
			TestManager.current_group[message] = func
		return func
	return decorator