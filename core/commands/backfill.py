from argparse import BooleanOptionalAction

from core.repository import SimulationRepository, Repository
from core.interval import Interval
from core.utils.time import normalize_timestamp, now
from core.utils.logging import Logger
from core.utils.serializer import RepresentationSerializer
from core.utils.command import CommandSession
from core.chart.command import ChartCommandSessionMixin

logger = Logger(__name__)

class BackfillCommandSession(
	ChartCommandSessionMixin,
	CommandSession
):
	def setup(self):
		super().setup()
		self.add_chart_fields_to_arguments(nargs = '*')
		self.parser.add_argument('repository', type = RepresentationSerializer(Repository).deserialize)
		self.parser.add_argument('--from', dest = 'from_timestamp', type = normalize_timestamp)
		self.parser.add_argument('--to', dest = 'to_timestamp', type = normalize_timestamp, default = now())
		self.parser.add_argument('--clean', action = BooleanOptionalAction, default = False)
		self.parser.add_argument('--workers', type = int, default = 5)
		self.parser.add_argument('--batch-size', type = RepresentationSerializer(Interval).deserialize, default = Interval.Month(1))

	def run(self):
		super().run()
		source_repository = self.args.repository()
		simulation_repository = SimulationRepository()

		if len(self.args.symbol) == 0:
			self.args.symbol = source_repository.get_available_symbols()

		for chart in source_repository.get_filtered_charts(
			filter = self.get_chart_filter_from_arguments()
		):
			simulation_repository.backfill(
				chart = chart,
				repository = self.args.repository,
				from_timestamp = self.args.from_timestamp,
				to_timestamp = self.args.to_timestamp,
				clean = self.args.clean,
				workers = self.args.workers,
				batch_size = self.args.batch_size
			)