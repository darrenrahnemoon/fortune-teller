from argparse import ArgumentParser, Namespace, BooleanOptionalAction

from core.repository import SimulationRepository, Repository
from core.utils.time import normalize_timestamp, now
from core.utils.logging import Logger
from core.utils.serializer import RepresentationSerializer
import core.utils.command.chart

logger = Logger(__name__)

def config(parser: ArgumentParser):
	core.utils.command.chart.add_fields_to_arguments(parser, nargs = '*')
	parser.add_argument('repository', type = RepresentationSerializer(Repository).deserialize)
	parser.add_argument('--from', dest = 'from_timestamp', type = normalize_timestamp)
	parser.add_argument('--to', dest = 'to_timestamp', type = normalize_timestamp, default = now())
	parser.add_argument('--clean', action = BooleanOptionalAction, default = False)
	parser.add_argument('--workers', type = int, default = 5)

def handler(args: Namespace):
	source_repository = args.repository()
	simulation_repository = SimulationRepository()

	if args.symbol[0] == '*':
		args.symbol = source_repository.get_available_symbols()

	for chart in source_repository.get_available_charts(
		filter = core.utils.command.chart.get_filter_from_arguments(args)
	):
		simulation_repository.backfill(
			chart = chart,
			repository = args.repository,
			from_timestamp = args.from_timestamp,
			to_timestamp = args.to_timestamp,
			clean = args.clean,
			workers = args.workers,
		)