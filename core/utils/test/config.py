from dataclasses import dataclass, field
from core.utils.config import Config

@dataclass
class TestStateConfig(Config):
	default: str = None
	success: str = None
	error: str = None
	skipped: str = None

@dataclass
class TestBlockConfig(Config):
	symbol: TestStateConfig = None
	color: TestStateConfig = None
	indentation_character: str = '  '

@dataclass
class TestCaseConfig(TestBlockConfig):
	symbol: TestStateConfig = field(
		default_factory = lambda: TestStateConfig(
			default = '▪',
			success = '✓',
			error = '×',
			skipped = '?',
		)
	)
	color: TestStateConfig = field(
		default_factory = lambda: TestStateConfig(
			default = 'cyan',
			success = 'green',
			error = 'red',
			skipped = 'yellow',
		)
	)

@dataclass
class TestGroupConfig(TestBlockConfig):
	symbol: TestStateConfig = field(
		default_factory = lambda: TestStateConfig(
			default = '▪',
			success = '✔',
			error = '⊗',
			skipped = '?',
		)
	)
	color: TestStateConfig = field(
		default_factory = lambda: TestStateConfig(
			default = None,
			success = 'green',
			error = 'red',
			skipped = 'yellow',
		)
	)

@dataclass
class TestManagerConfig(Config):
	test_group: TestGroupConfig = field(default_factory = TestGroupConfig)
	test_case: TestCaseConfig = field(default_factory = TestCaseConfig)