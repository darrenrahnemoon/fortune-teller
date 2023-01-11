import argparse

from core.repository import Repository, SimulationRepository
from core.chart import Chart
from core.utils.time import normalize_timestamp, now
from core.utils.cls import pretty_repr, product_dict
from core.utils.command import Command
from core.utils.command.serializers import CommandArgumentSerializer
from core.utils.logging import logging

logger = logging.getLogger(__name__)

class BackfillHistoricalDataCommand(Command):
	def config(self):
		self.parser.add_argument(
			'--symbol',
			nargs = '*',
			default = []
		)
		self.parser.add_argument(
			'--repository',
			type = CommandArgumentSerializer(Repository).deserialize
		)
		self.parser.add_argument(
			'--chart',
			nargs = '*',
			type = CommandArgumentSerializer(Chart).deserialize
		)
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

		for chart_class in [ Chart ] + Chart.__subclasses__():
			self.add_arguments_from_class(
				cls = chart_class,
				select = chart_class.query_fields,
				kwargs = {
					'nargs' : '*'
				}
			)

	def handler(self):
		if not self.args.repository:
			logger.error('You need to specify a repository to backfill from.')
			return
		source_repository = self.args.repository()
		simulation_repository = SimulationRepository()

		if self.args.symbol[0] == '*':
			symbols = set()
			for _, combinations in source_repository.get_available_chart_combinations().items():
				for combination in combinations:
					for symbol in combination['symbol']:
						symbols.add(symbol)
			self.args.symbol = list(symbols)

		combinations = {
			key: value
			for key, value in self.args.__dict__.items() 
			if key not in [ 'workers', 'repository', 'from_timestamp', 'to_timestamp', 'clean' ] and value != None
		}

		for chart in source_repository.get_available_charts(filter = combinations):
			simulation_repository.backfill(
				chart = chart,
				repository = self.args.repository,
				from_timestamp = self.args.from_timestamp,
				to_timestamp = self.args.to_timestamp,
				clean = self.args.clean,
				workers = self.args.workers,
			)