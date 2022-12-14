from core.broker.simulation import SimulationBroker
import functools
import math
from re import S
import numpy
import pandas
from dataclasses import dataclass

from keras import Model
from keras.layers import Input, Dense, Conv1D, Add, Dropout, Flatten, LSTM, Reshape
from keras_tuner import HyperParameters

from core.chart import ChartGroup, CandleStickChart
from .repository import NextPeriodHighLowRepository

@dataclass
class NextPeriodHighLow:
	repository = NextPeriodHighLowRepository()

	def __init__(
		self,
		chart_group: ChartGroup,
		trading_focus: list[CandleStickChart],
		forward_window_length: int,
		backward_window_length: int,
	):
		self.chart_group = chart_group
		self.trading_focus = trading_focus
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

	def prepare_dataset(self, increments = 100):
		if self.repository.has_dataset(self.chart_group):
			return
		common = SimulationBroker.get_common_period(self.chart_group)
		self.chart_group.set_field('to_timestamp', None)
		self.chart_group.set_field('count', increments)
		timestamp = common.from_timestamp
		while (timestamp < common.to_timestamp):
			self.chart_group.set_field('from_timestamp', timestamp)
			self.chart_group.read()
			print(self.chart_group.dataframe)
			self.preprocess_input(self.chart_group)
			print(self.chart_group.dataframe)
			timestamp = self.chart_group.dataframe.index[-increments]
			# if len(self.chart_group.dataframe) < self.backward_window_size:
			# 	break

	@classmethod
	def preprocess_input(self, chart_group: ChartGroup = None) -> ChartGroup:
		for chart in chart_group.charts:
			data: pandas.DataFrame = chart.data
			data = data.interpolate(method='linear')
			data = data.pct_change()
			chart.data = data
			chart.refresh_indicators()

		dataframe = chart_group.dataframe
		dataframe = dataframe.fillna(0)
		chart_group.dataframe = dataframe

	@property
	@functools.cache
	def input_features_length(self):
		input_features_length = 0
		for chart in self.chart_group.charts:
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
		return (
			len(self.trading_focus),
			2 # [ High, Low ]
		)