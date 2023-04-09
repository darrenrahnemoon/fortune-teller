import traceback
from typing import Callable, TYPE_CHECKING
from termcolor import colored
from dataclasses import dataclass

from core.utils.test.blocks.block import TestBlock
from core.utils.test.stats import TestStats
if TYPE_CHECKING:
	from .group import TestGroup

@dataclass
class TestCase(TestBlock):
	handler: Callable = None
	parent: 'TestGroup' = None

	def run(
		self,
		filter_name: str = '',
		force_skip: bool = False,
	):
		if force_skip or (filter_name not in self.name):
			self.print(status = 'skipped', metadata = [ 'skipped' ])
			return TestStats(skipped = 1)

		try:
			self.print(status = 'default', end = '\r')
			_, elapsed_time = self.run_and_measure_time(self.handler)
			self.print(status = 'success', metadata = [ elapsed_time ])
			return TestStats(success = 1)
		except Exception:
			self.print(
				colored(f'\n{traceback.format_exc()}', color = self.config.color.error),
				status = 'error'
			)
			return TestStats(error = 1)