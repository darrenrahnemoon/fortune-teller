from dataclasses import dataclass, field
from termcolor import colored
from core.utils.test.blocks.group import TestGroup
from core.utils.test.blocks.case import TestCase
from core.utils.test.config import TestManagerConfig
from core.utils.module import import_modules

@dataclass
class TestManager:
	config: TestManagerConfig = field(default_factory = TestManagerConfig)
	root: TestGroup = field(
		default_factory = lambda: TestGroup(
			name = 'All Tests'
		)
	)
	cursor: TestGroup = field(init = False, repr = False, default = None)

	def __post_init__(self):
		self.cursor = self.root

	def group(
		self,
		name: str = '',
		skip: bool = False,
	):
		def wrapper(load_test_cases):
			test_group = TestGroup(
				name = name,
				skip = skip,
				config = self.config.test_group,
			)
			self.cursor.add_child(test_group)
			self.cursor = test_group
			load_test_cases()
			self.cursor = self.cursor.parent
		return wrapper

	def case(
		self,
		name: str = '',
		skip: bool = False,
	):
		def wrapper(handler):
			test_case = TestCase(
				name = name,
				skip = skip,
				handler = handler,
				config = self.config.test_case,
			)
			self.cursor.add_child(test_case)
		return wrapper

	def before(self):
		def wrapper(hook):
			self.cursor.before.append(hook)
		return wrapper

	def before_each(self):
		def wrapper(hook):
			self.cursor.before_each.append(hook)
		return wrapper

	def after(self):
		def wrapper(hook):
			self.cursor.after.append(hook)
		return wrapper

	def after_each(self):
		def wrapper(hook):
			self.cursor.after_each.append(hook)
		return wrapper

	def load_files(self, patterns: list[str]):
		import_modules(patterns)

	def run(
		self,
		filter_name: str = ''
	):
		stats = self.root.run(
			filter_name = filter_name
		)
		print(colored('Summary:', attrs = [ 'bold' ]))
		print(colored(f'Success: {stats.success}', color = self.config.test_case.color.success ))
		print(colored(f'Error: {stats.error}', color = self.config.test_case.color.error ))
		print(colored(f'Skipped: {stats.skipped}', color = self.config.test_case.color.skipped ))