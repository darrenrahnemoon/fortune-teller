from dependency_injector.providers import Container, Configuration
from dependency_injector.containers import DeclarativeContainer
from core.utils.container import to_dependency_injector_configuration
from examples.ave_maria.tensorflow.container import AveMariaTensorflowContainer
from examples.ave_maria.trading.container import AveMariaTradingContainer

class AveMariaContainer(DeclarativeContainer):
	config = Configuration()
	tensorflow = Container(
		AveMariaTensorflowContainer,
		config = config.tensorflow.as_(to_dependency_injector_configuration),
		trading_config = config.trading.as_(to_dependency_injector_configuration),
	)
	trading = Container(
		AveMariaTradingContainer,
		config = config.trading.as_(to_dependency_injector_configuration),
		tensorflow = tensorflow,
	)

