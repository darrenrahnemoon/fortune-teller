from dependency_injector.providers import Singleton, DependenciesContainer, Configuration
from dependency_injector.containers import DeclarativeContainer

from apps.ave_maria.trading.strategy import AveMariaStrategy
from apps.ave_maria.trading.config import AveMariaTradingConfig

class AveMariaTradingContainer(DeclarativeContainer):
	config = Configuration()
	config_cls = AveMariaTradingConfig
	tensorflow = DependenciesContainer()

	strategy = Singleton(
		AveMariaStrategy,
		config = config.dataclass,
		trainer_service = tensorflow.trainer_service,
		tuner_service = tensorflow.tuner_service,
		predictor_service = tensorflow.predictor_service,
	)
