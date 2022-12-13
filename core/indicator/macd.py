import pandas
from dataclasses import dataclass

from core.indicator.indicator import Indicator

@dataclass
class MACDIndicator(Indicator):
	query_fields = [ 'window_slow', 'window_fast' ]
	value_fields = [ 'value' ]

	window_slow: float = None
	window_fast: float = None

	def run(self, dataframe: pandas.DataFrame):
		exp1 = dataframe['close'].ewm(span=self.window_slow, adjust=False).mean()
		exp2 = dataframe['close'].ewm(span=self.window_fast, adjust=False).mean()
		return exp1 - exp2
