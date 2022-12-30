import argparse
import logging
import pandas

from core.repository import Repository, SimulationRepository
from core.chart import Chart
from core.utils.time import normalize_timestamp, now
from core.utils.cls import product_dict
from core.utils.command import Command
from core.utils.command.serializers import CommandArgumentSerializer

logger = logging.getLogger(__name__)

class BackfillHistoricalDataCommand(Command):
	def config(self):
		self.parser.add_argument(
			'symbol',
			nargs = '*',
			default = []
		)
		self.parser.add_argument(
			'--data-provider',
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
			logger.error('You need to specify a data provider to backfill from.')
			return

		source_repository: Repository = self.args.repository()
		simulation_repository = SimulationRepository()
		combinations = {
			key: value
			for key, value in self.args.__dict__.items() 
			if key not in [ 'repository', 'from_timestamp', 'to_timestamp', 'clean' ] and value != None
		}

		for combination in product_dict(combinations):
			increments = []
			chart_class = combination.pop('chart')
			chart = chart_class(repository = source_repository, **combination)
			increments = list(pandas.date_range(
				start = self.args.from_timestamp,
				end = self.args.to_timestamp,
				freq = 'MS' # "Month Start"
			))
			increments.append(self.args.to_timestamp)
			if len(increments) == 1:
				increments.insert(0, self.args.from_timestamp)
			if self.args.clean:
				simulation_repository.remove_historical_data(chart)
			for index in range(1, len(increments)):
				chart.from_timestamp = increments[index - 1]
				chart.to_timestamp = increments[index]
				logger.info(f'Backfilling chart:\n{chart}')
				chart.read()
				simulation_repository.write_chart(chart)
