import functools
import math
import pandas
from typing import Callable
from dataclasses import dataclass

from keras import Model
from keras.layers import Input, Dense, Conv1D, Add, Dropout, Flatten, LSTM, Reshape
from keras_tuner import HyperParameters

from core.chart import ChartGroup, Chart
from core.broker import SimulationBroker
from .repository import NextPeriodHighLowRepository
from core.utils.math import mean_normalize

@dataclass
class NextPeriodHighLow:
	repository = NextPeriodHighLowRepository()

	def __init__(
		self,
		build_chart_group: Callable[..., tuple[ChartGroup, list[Chart]]],
		forward_window_length: int,
		backward_window_length: int,
	):
		self.build_chart_group = build_chart_group
		self.backward_window_length = backward_window_length
		self.forward_window_length = forward_window_length

	def build_model(self, parameters: HyperParameters):
		x = Input(
			shape=self.input_shape,
			batch_size=parameters.Choice('batch_size', [ 2 ** size for size in range(4, 15) ]),
		)

		dropout_rate = parameters.Float('dropout_rate', min_value=0.2, max_value=0.7, step=0.05)
		parallel_cnns_count = parameters.Int('parallel_cnns_count', min_value=2, max_value=15)
		filters_count = parameters.Int('filters_count', min_value=2 ** 3, max_value=2 ** 10)
		lstm_units = parameters.Int('lstm_units', min_value=2 ** 4, max_value=2**10)

		y = []
		for index in range(parallel_cnns_count):
			_y = Conv1D(filters=filters_count, kernel_size=2 ** (index + 4), padding='same')(x)
			_y = Dropout(dropout_rate)(_y)

			_y = Conv1D(filters=filters_count, kernel_size=2 ** (index + 2), padding='same')(_y)
			_y = Dropout(dropout_rate)(_y)

			_y = LSTM(lstm_units)(_y)
			_y = Dropout(dropout_rate)(_y)

			y.append(_y)
		y = Add()(y)
		y = Flatten()(y)

		flattened_output_length = math.prod(*self.output_shape)
		for _ in range(parameters.Int('fully_connected_layer_count', min_value=2, max_value=5)):
			y = Dense((y.shape[1] - flattened_output_length) * 2 / 3)(y)
			y = Dropout(dropout_rate)(y)

		y = Dense(flattened_output_length)(y)
		y = Reshape(self.output_shape)

		model = Model(inputs=x, outputs=y)
		model.compile(
			optimizer=parameters.Choice('optimizer', [ 'adam', 'sdg' ]),
			loss='mse',
			metrics=[ 'accuracy' ]
		)
		return model

	def cache_dataset(self, overwrite = False, batch_size = 1000):
		chart_group, trading_focus = self.build_chart_group()

		collection = self.repository.get_collection_for_chart_group(chart_group)
		if collection.count_documents({}) > 0:
			if overwrite:
				collection.drop()
			else:
				return

		total_window_length = self.backward_window_length + self.forward_window_length

		chart_group.set_fields({
			'from_timestamp': None,
			'to_timestamp': None,
			'count': total_window_length * 2,
		})

		common_time_window = SimulationBroker.get_common_time_window(chart_group)
		timestamp = common_time_window.from_timestamp
		while (timestamp < common_time_window.to_timestamp):
			chart_group.set_field('from_timestamp', timestamp)
			chart_group.read()

			self.preprocess_input(chart_group, is_production=False)
			collection.insert_many(dataset_items.dataframe.)
			if len(chart_group.dataframe) < total_window_length:
				break
			timestamp = chart_group.dataframe.index[1]

	def preprocess_input(
		self,
		chart_group: ChartGroup = None,
		is_production = True
	):
		for chart in chart_group.charts:
			data: pandas.DataFrame = chart.data
			data = data.interpolate(method='linear')
			data = data.pct_change()
			chart.data = data
			chart.refresh_indicators()

		dataframe = chart_group.dataframe
		dataframe = mean_normalize(dataframe)
		if is_production:
			if len(dataframe) < self.backward_window_length:
				# Pad dataframe
				pass
			elif len(dataframe) > self.backward_window_length:
				dataframe = dataframe.tail(self.backward_window_length)
		dataframe = dataframe.fillna(0)
		chart_group.dataframe = dataframe

	def to_dataset_item(self, chart_group: ChartGroup, trading_focus: list[Chart]):
		result = dict()
		result['input'] = mean_normalize(chart_group.dataframe[:self.backward_window_length]).values.tolist()
		result['output'] = []
		for chart in trading_focus:
			data = chart.data[-self.forward_window_length:]
			result['output'].append([
				data['high'].max(),
				data['low'].min()
			])
		return result

	@property
	@functools.cache
	def input_features_length(self):
		chart_group, = self.build_chart_group()
		input_features_length = 0
		for chart in chart_group.charts:
			input_features_length += len(chart.select)
			for indicator in chart.indicators.values():
				input_features_length += len(indicator.value_fields)
		return input_features_length

	@property
	@functools.cache
	def input_shape(self):
		return (
			self.backward_window_length,
			self.input_features_length
		)

	@property
	@functools.cache
	def output_shape(self):
		_, trading_focus = self.build_chart_group()
		return (
			len(trading_focus),
			2 # [ High, Low ]
		)