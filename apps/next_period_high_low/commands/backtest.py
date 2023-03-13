import pandas
from argparse import ArgumentParser, Namespace

from apps.next_period_high_low.container import NextPeriodHighLowContainer
from apps.next_period_high_low.config import NextPeriodHighLowConfig

from core.broker.simulation import SimulationBroker
from core.utils.time import normalize_timestamp, now
import core.utils.command.config

def config(parser: ArgumentParser):
	core.utils.command.config.add_fields_to_arguments(parser, NextPeriodHighLowConfig)
	parser.add_argument('--timestamp', default = now(), type = normalize_timestamp)
	parser.add_argument('--from', dest = 'from_timestamp', default = now() - pandas.Timedelta(365, 'day'), type = normalize_timestamp)
	parser.add_argument('--to', dest = 'to_timestamp', default = now(), type = normalize_timestamp)

def handler(args: Namespace):
	config = core.utils.command.config.set_fields_from_arguments(args, NextPeriodHighLowConfig())
	container = NextPeriodHighLowContainer(config = config)

	strategy = container.strategy()
	broker: SimulationBroker = config.strategy.metatrader_broker
	broker.timesteps = pandas.date_range(
		args.from_timestamp,
		args.to_timestamp,
		freq = config.strategy.interval.to_pandas_frequency()
	)
	broker.backtest(strategy)