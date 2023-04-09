import traceback
from time import time
from typing import Callable, Literal
from dataclasses import dataclass, field

from core.utils.test.blocks.case import TestCase
from core.utils.test.stats import TestStats
from core.utils.test.blocks.block import TestBlock

@dataclass
class TestGroup(TestBlock):
	before: list[Callable] = field(default_factory = list)
	before_each: list[Callable] = field(default_factory = list)
	after: list[Callable] = field(default_factory = list)
	after_each: list[Callable] = field(default_factory = list)

	parent: 'TestGroup' = None
	children: list['TestGroup' or TestCase] = field(default_factory = list)

	def add_child(self, child: 'TestGroup' or TestCase):
		child.parent = self
		child.level = self.level + 1
		self.children.append(child)

	def run(
		self,
		filter_name: str = '',
		force_skip: bool = False,
	) -> TestStats:
		if self.skip:
			force_skip = True
		if force_skip:
			self.print(status = 'skipped', metadata = [ 'skipped' ])
		else:
			self.print(status = 'default')
		test_group_stats = self.run_children(
			filter_name = filter_name,
			force_skip = force_skip,
		)
		return test_group_stats

	def run_children(
		self,
		filter_name: str = '',
		force_skip: bool = False,
	):
		# If filter requirement is satisfied by this TestGroup all children must run
		if filter_name in self.name:
			filter_name = ''

		test_group_stats = TestStats()

		self.run_hooks(
			name = 'before',
			skip = force_skip or self.skip
		)

		for test_case in self.children:
			self.run_hooks(
				name = 'before_each',
				skip = force_skip or test_case.skip
			)

			test_case_stats = test_case.run(
				filter_name = filter_name,
				force_skip = force_skip
			)
			test_group_stats += test_case_stats

			self.run_hooks(
				name = 'after_each',
				skip = force_skip or test_case.skip
			)

		self.run_hooks(
			name = 'after',
			skip = force_skip or self.skip
		)

		return test_group_stats

	def run_hooks(
		self,
		name: Literal['before', 'before_each', 'after', 'after_each'],
		skip: bool = False
	):
		if skip:
			return
		for hook in getattr(self, name):
			try:
				hook()
			except Exception as exception:
				self.print(
					f"'{name}' hook raised an exception:\n{exception}\n{traceback.format_exc()}",
					status = 'error'
				)