# Charts

Charts are at the heart of the Fortune Teller library. They encapsulate the structure of the financial data on the class level, the query that lead to acquiring the financial data and the data itself on the instance level.

## Common Querying Parameters
* `symbol`: the name of the instrument or data being queried 
* `from_timestamp`: Inclusive starting point of the time period being queried
* `to_timestamp`: Inclusive end point of the time period being queried
* `count`: number of data points to query. Must be used with either `from_timestamp` or `to_timestamp`. 
* `select`: list of columns that are needed. Everything else is omitted. 

## CandleStick Chart
CandleStickChart is a common chart type for periodic financial data with fields such as `Open`, `High`, `Low`, `Close` baked in.

### Example
```python
from fortune_teller.core.trading.repository import MetaTraderRepository
from fortune_teller.core.trading.chart import CandleStickChart
from fortune_teller.core.trading.interval import Interval

repository = MetaTraderRepository()
chart = CandleStickChart(
	symbol = "AAPL",
	from_timestamp = "2020-02-01 10:00:12 UTC",
	to_timestamp = "2024-04-21 12:21:12", # Or alternatively leave blank to default to "now"
	interval = Interval.Minute(5),
	repository = repository,
)
chart.read()
print(chart.data)
```

## Line Chart
LineChart is a chart type with only one value, commonly used for economical indicators, etc.

### Example
```python
from fortune_teller.core.trading.repository import AlphaVantageRepository
from fortune_teller.core.trading.chart import LineChart
from fortune_teller.core.trading.interval import Interval

repository = AlphaVantageRepository()
chart = LineChart(
	symbol = 'TREASURY_YIELD',
	repository = repository,
	interval = Interval.Day(1),
	maturity = Interval.Year(30)
)
chart.read()
print(chart.data)
```

## Tick Chart
TickChart is a common chart type used for encapsulating market tick data with fields such as `Bid`, `Ask`, `Last` baked in.

### Example
```python
from fortune_teller.core.trading.repository import MetaTraderRepository
from fortune_teller.core.trading.chart import TickChart

repository = MetaTraderRepository()
chart = TickChart(
	symbol = "AAPL",
	from_timestamp = "2020-02-01 10:00:12 UTC",
	to_timestamp = "2024-02-21 12:21:12",
	repository = repository,
)
chart.read()
print(chart.data)
```


**Note:** Should you need a custom chart type with specific data fields you can extend the base `Chart` class and replicate the pattern from one of the other implemented chart types to define your query parameters and the data structure for each record in the financial data acquired. See example [here](./types/candlestick.py).

**Note:** Since Charts are wrappers for `pandas.DataFrames` that add additional capabilities to them it might be tempting to put derived columns directly inside the dataframe. Please use `Indicators` for adding any columns that needs to be derived.