import humanize
from dataclasses import dataclass
from time import time
from termcolor import colored
from core.utils.test.config import TestBlockConfig

@dataclass
class TestBlock:
	name: str = ''
	skip: bool = False
	level: int = 0
	config: TestBlockConfig = None

	def run_and_measure_time(self, func, *args, **kwargs):
		start_time = time()
		result = func(*args, **kwargs)
		end_time = time()
		elapsed_time = start_time - end_time
		elapsed_time = humanize.precisedelta(elapsed_time, minimum_unit = 'microseconds')
		return result, elapsed_time

	def print(self, *args, metadata: list[str] = [], status = 'default', **kwargs):
		color = getattr(self.config.color, status)
		symbol = getattr(self.config.symbol, status)
		print(
			f'{self.level * self.config.indentation_character}',
			colored(symbol, color = color),
			self.name,
			*[ colored(f"[{data}]", color = color) for data in metadata ],
			*args,
			**kwargs
		)

	def print_start(self):
		self.print(
			colored(self.config.symbol, color = self.config.color.default),
			f'{self.name}...',
			end = '\r'
		)

	def print_success(
		self,
		elapsed_time: float = None
	):
		elapsed_time = self.to_human_friendly_time(elapsed_time)
		self.print(
			colored(self.config.symbol, color = self.config.color.success),
			self.name,
			metadata = [
				{
					'value': elapsed_time,
					'color': self.config.color.success,
				}
			]
		)

	def print_error(
		self,
		error: str,
		elapsed_time: float = None,
	):
		self.print(
			colored(self.config.symbol, color = self.config.color.error),
			self.name,
			error,
			metadata = [
				{
					'value': elapsed_time,
					'color': self.config.color.error,
				}
			]
		)

	def print_skipped(self):
		self.print(
			colored(self.config.symbol, color = self.config.color.skipped),
			self.name,
			colored('[Skipped]', color = self.config.color.skipped),
		)