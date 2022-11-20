import pandas

from lib.indicator.indicator import Indicator

class MACDIndicator(Indicator):
	def run(self, dataframe: pandas.DataFrame):
		exp1 = dataframe['close'].ewm(span=self.window_slow, adjust=False).mean()
		exp2 = dataframe['close'].ewm(span=self.window_fast, adjust=False).mean()
		return exp1 - exp2
