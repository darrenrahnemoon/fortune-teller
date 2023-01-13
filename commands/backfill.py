import argparse

from core.repository import SimulationRepository
from core.utils.time import normalize_timestamp, now
from core.utils.logging import logging
from core.utils.command import Command
from .chart_filter import ChartFilterCommand

logger = logging.getLogger(__name__)

@Command.register
class BackfillHistoricalDataCommand(ChartFilterCommand):
	def config(self):
		self.add_chart_arguments(nargs = '*')
		self.parser.add_argument(
			'--from',
			dest = 'from_timestamp',
			type = normalize_timestamp
		)
		self.parser.add_argument(
			'--to',
			dest = 'to_timestamp',
			default = now(),
			type = normalize_timestamp
		)
		self.parser.add_argument(
			'--clean',
			action = argparse.BooleanOptionalAction
		)
		self.parser.add_argument(
			'--workers',
			default = 5,
			type = int,
		)

	def handler(self):
		if not self.args.repository:
			logger.error('You need to specify a repository to backfill from.')
			return
		source_repository = self.args.repository()
		simulation_repository = SimulationRepository()

		if self.args.symbol[0] == '*':
			self.args.symbol = source_repository.get_available_symbols()

		for chart in source_repository.get_available_charts(filter = self.get_chart_filter()):
			simulation_repository.backfill(
				chart = chart,
				repository = self.args.repository,
				from_timestamp = self.args.from_timestamp,
				to_timestamp = self.args.to_timestamp,
				clean = self.args.clean,
				workers = self.args.workers,
			)