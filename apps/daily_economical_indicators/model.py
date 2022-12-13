import functools
import numpy
import pandas

from keras import Model
from keras.layers import Input, Dense, Conv1D, Add, Dropout, Flatten, LSTM
from keras_tuner import HyperModel, HyperParameters

from core.chart import ChartGroup, CandleStickChart
from core.interval import Interval

class NextPeriodHighLowModel(HyperModel):
	def __init__(
		self,
		chart_group: ChartGroup = None,
		trading_focus: CandleStickChart = None,
		forward_window_interval: Interval = None,
		backward_window_interval: Interval = None,
	):
		super().__init__()
		self.chart_group = chart_group
		self.trading_focus = trading_focus
		self.forward_window_interval = forward_window_interval
		self.backward_window_interval = backward_window_interval
		self.output_length = 2

	def build(self, parameters: HyperParameters):
		x = Input(
			shape=(
				self.backward_window_length,
				self.features_length
			),
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
		for _ in range(parameters.Int('fully_connected_layer_count', min_value=2, max_value=5)):
			y = Dense((y.shape[1] - self.output_length) * 2 / 3)(y)
			y = Dropout(dropout_rate)(y)
		y = Dense(self.output_length)(y)
		return Model(inputs=x, outputs=y)

	def preprocess_input(self, chart_group: ChartGroup) -> ChartGroup:
		for chart in chart_group.charts:
			data: pandas.DataFrame = chart.data
			data = data.interpolate(method='linear')
			data = data.pct_change()
			chart.data = data
			chart.refresh_indicators()

		dataframe = chart_group.dataframe
		dataframe = dataframe.fillna(0)
		chart_group.dataframe = dataframe
		return chart_group

	def preprocess_output(self, chart: CandleStickChart):
		data = chart.data
		origin = data['open'].iloc[0]
		return numpy.array([ data['high'].max() / origin - 1, data['low'].min() / origin - 1 ])

	@property
	@functools.cache
	def features_length(self):
		features_length = 0
		for chart in self.chart_group.charts:
			features_length += len(chart.select)
			for indicator in chart.indicators.values():
				features_length += len(indicator.value_fields)
		return features_length

	@property
	@functools.cache
	def backward_window_length(self) -> int:
		return int(self.backward_window_interval.to_pandas_timedelta() / self.trading_focus.interval.to_pandas_timedelta())
