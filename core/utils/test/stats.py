from dataclasses import dataclass

@dataclass
class TestStats:
	success: int = 0
	error: int = 0
	skipped: int = 0

	@property
	def total(self):
		return self.success + self.error + self.skipped

	def __add__(self, other: 'TestStats'):
		return TestStats(
			success = self.success + other.success,
			error = self.error + other.error,
			skipped = self.skipped + other.skipped,
		)
