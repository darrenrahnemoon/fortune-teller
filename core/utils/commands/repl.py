# A set of common classes preloaded for REPL
from core.utils.environment import *
from core.utils.time import *
from core.utils.cls import *
from core.utils.collection import *
from core.utils.math import *
from core.utils.config import *
from core.utils.command import CommandSession

from core.trading.chart import *
from core.trading.indicator import *
from core.trading.broker import *
from core.trading.repository import *
from core.trading.interval import *
from core.trading.size import *
from core.trading.order import *
from core.trading.position import *

if is_windows:
	metatrader_broker = MetaTraderBroker()
	metatrader_repository = metatrader_broker.repository

simulation_broker = SimulationBroker()
simulation_repository = simulation_broker.repository

class REPLCommandSession(CommandSession):
	def run(self):
		super().run()
		print('Use `./repl.sh` to run this command.')
