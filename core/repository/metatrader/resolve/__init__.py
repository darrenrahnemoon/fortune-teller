from core.utils.environment import is_windows
from core.utils.module import import_module

# HACK for MetaTraderRepository
# Intentionally imported this way so that importing this package on MacOS and Linux doesn't bork about MetaTrader5 which is only available on Windows
if not is_windows:
	import_module('core.repository.metatrader.resolve.MetaTrader5', to_path = 'MetaTrader5')