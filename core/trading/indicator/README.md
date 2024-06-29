# Indicators
Indicators encapsulate derived data based on a chart's data. Indicators can be used for technical analysis.

## Defining an Indicator
You can define an indicator by subclassing `Indicator` and implementing the necessary methods.

### Example
```python
import pandas
from dataclasses import dataclass

from fortune_teller.core.trading.repository import MetaTraderRepository
from fortune_teller.core.trading.chart import CandleStickChart
from fortune_teller.core.trading.interval import Interval
from fortune_teller.core.trading.indicator import Indicator


@dataclass
class MACDIndicator(Indicator):
	window_slow: float = None
	window_fast: float = None

	@dataclass
	class Record(Indicator.Record):
		value: float = None

	def run(self, dataframe: pandas.DataFrame):
		# Note: do NOT mutate the dataframe provided
		exp1 = dataframe['close'].ewm(span=self.window_slow, adjust=False).mean()
		exp2 = dataframe['close'].ewm(span=self.window_fast, adjust=False).mean()
		return exp1 - exp2 # Return the dataframe or series you'd like this indicator to represent
```

## Using Indicators on Charts

Indicators can be either defined immediately when querying from a chart or added to a chart later once data is loaded.

#### Defining Indicators During Querying
```python
repository = MetaTraderRepository()
chart = CandleStickChart(
	symbol = "AAPL",
	from_timestamp = "2020-02-01 10:00:12 UTC",
	to_timestamp = "2024-04-21 12:21:12", # Or alternatively leave blank to default to "now"
	interval = Interval.Minute(5),
	repository = repository,
	indicators = {
		'my_cool_indicator': MACDIndicator(window_slow = 10, window_fast = 5)
	}
)
chart.read()
print(chart.data)
print(chart.indicators['my_cool_indicator'].data)
```

#### Attaching Indicators After Chart is Loaded
```python
repository = MetaTraderRepository()
chart = CandleStickChart(
	symbol = "AAPL",
	from_timestamp = "2020-02-01 10:00:12 UTC",
	to_timestamp = "2024-04-21 12:21:12", # Or alternatively leave blank to default to "now"
	interval = Interval.Minute(5),
	repository = repository,
)
chart.read()
chart.attach_indicator(
	MACDIndicator(window_slow = 10, window_fast = 5),
	name = 'my_other_cool_indicator'
)

print(chart.data)
print(chart.indicators['my_cool_indicator'].data)
```