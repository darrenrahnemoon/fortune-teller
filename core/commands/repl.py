# A set of common classes preloaded for REPL
from core.utils.environment import *
from core.utils.time import *
from core.utils.cls import *
from core.utils.collection import *
from core.utils.math import *
from core.utils.config import *

from core.chart import *
from core.indicator import *
from core.broker import *
from core.repository import *
from core.interval import *
from core.size import *
from core.order import *
from core.position import *
if is_windows:
	metatrader_broker = MetaTraderBroker()
	metatrader_repository = metatrader_broker.repository

simulation_broker = SimulationBroker()
simulation_repository = simulation_broker.repository

def handler(args):
	print('Use `./repl.sh` to run this command.')