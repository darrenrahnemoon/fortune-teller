
from core.utils.tensorflow.sequence.batched import BatchedSequence
from core.chart.serializers import MULTI_INDEX_COLUMN_SEPARATOR
from typing import Callable
from dataclasses import dataclass, field
from caseconverter import snakecase

import tensorflow
from keras import Model
from keras.layers import Input, Dense, Conv1D, Add, Dropout, Flatten, LSTM, Concatenate
from keras.callbacks import EarlyStopping
from keras_tuner import HyperParameters, Hyperband

from core.chart import ChartGroup
from .preprocessor import NextPeriodHighLowPreprocessor
from .repository import NextPeriodHighLowRepository
from .sequence import NextPeriodHighLowSequence
from core.utils.environment import project_directory
from core.utils.tensorflow.sequence import ShuffledSequence, PartialSequence

@dataclass
class NextPeriodHighLowModelService:
	build_input_chart_group: Callable[..., ChartGroup] = None
	build_output_chart_group: Callable[..., ChartGroup] = None
	dataset: NextPeriodHighLowSequence = field(init = False)

	forward_window_length: int = None
	backward_window_length: int = None
	batch_size: int = 128
	validation_split: float = 0.3

	def __post_init__(self):
		preprocessor = NextPeriodHighLowPreprocessor(
			forward_window_length = self.forward_window_length,
			backward_window_length = self.backward_window_length
		)
		repository = NextPeriodHighLowRepository(
			preprocessor = preprocessor
		)
		dataset = NextPeriodHighLowSequence(
			build_input_chart_group = self.build_input_chart_group,
			build_output_chart_group = self.build_output_chart_group,
			forward_window_length = self.forward_window_length,
			backward_window_length = self.backward_window_length,
			repository = repository,
			preprocessor = preprocessor
		)
		dataset = ShuffledSequence(dataset)
		training_dataset = PartialSequence(
			sequence = dataset,
			portion = 1 - self.validation_split
		)
		self.training_dataset = BatchedSequence(
			sequence = training_dataset,
			batch_size = self.batch_size
		)
		validation_dataset = PartialSequence(
			sequence = dataset,
			offset = 1 - self.validation_split,
			portion = self.validation_split
		)
		self.validation_dataset = BatchedSequence(
			sequence = validation_dataset,
			batch_size = self.batch_size
		)

	def train(self):
		tuner = Hyperband(
			hypermodel = self.build_model,
			objective = 'val_loss',
			max_epochs = 10,
			factor = 3,
			directory = project_directory.joinpath('models'),
			project_name = snakecase(type(self).__name__)
		)
		tuner.search(
			self.training_dataset,
			validation_data = self.validation_dataset,
			epochs = 50,
			batch_size = self.batch_size,
			validation_batch_size = self.batch_size,
			callbacks = [
				EarlyStopping(monitor='val_loss', patience=5)
			]
		)
		best = tuner.get_best_hyperparameters(num_trials=1)[0]

	def build_model(self, parameters: HyperParameters):
		inputs = self.build_model_inputs()
		x = Concatenate(axis = 2)(inputs)

		dropout_rate = parameters.Float('dropout_rate', min_value = 0.2, max_value = 0.7, step = 0.05)
		parallel_cnns_count = parameters.Int('parallel_cnns_count', min_value = 2, max_value = 15)
		filters_count = parameters.Int('filters_count', min_value = 2 ** 3, max_value = 2 ** 10)
		lstm_units = parameters.Int('lstm_units', min_value = 2 ** 4, max_value = 2**10)

		y = []
		for index in range(parallel_cnns_count):
			_y = Conv1D(filters = filters_count, kernel_size = 2 ** (index + 4), padding = 'same')(x)
			_y = Dropout(dropout_rate)(_y)

			_y = Conv1D(filters = filters_count, kernel_size = 2 ** (index + 2), padding = 'same')(_y)
			_y = Dropout(dropout_rate)(_y)

			_y = LSTM(lstm_units)(_y)
			_y = Dropout(dropout_rate)(_y)

			y.append(_y)
		y = Add()(y)
		y = Flatten()(y)

		for index in range(parameters.Int('fully_connected_layer_count', min_value = 2, max_value = 5)):
			y = Dense(parameters.Int(f'fully_connected_layer_{index}_nodes', min_value = 2 ** 6, max_value = 2 ** 14))(y)
			y = Dropout(dropout_rate)(y)

		outputs = self.build_model_outputs(y)
		model = Model(
			inputs = inputs,
			outputs = outputs
		)
		model.compile(
			optimizer = parameters.Choice('optimizer', [ 'adam', 'sgd' ]),
			loss = 'mse',
			metrics = [ 'accuracy' ]
		)
		return model

	def build_model_inputs(self):
		input_chart_group = self.build_input_chart_group()
		inputs = []
		def define_input_fields(time_series, fields):
			for field in fields:
				name = f'{time_series}{MULTI_INDEX_COLUMN_SEPARATOR}{field}'
				inputs.append(
					Input(
						name = name,
						shape = (self.backward_window_length, 1),
						batch_size = self.batch_size,
						dtype = tensorflow.float64
					)
				)

		for chart in input_chart_group.charts:
			define_input_fields(chart.name, chart.select)
			for indicator in chart.indicators.values():
				define_input_fields(indicator.name, indicator.value_fields)
		return inputs

	def build_model_outputs(self, x):
		outputs = {}
		output_chart_group = self.build_output_chart_group()
		for chart in output_chart_group.charts:
			outputs[(chart.name, 'high')] = Dense(1)(x)
			outputs[(chart.name, 'low')] = Dense(1)(x)
		return outputs
