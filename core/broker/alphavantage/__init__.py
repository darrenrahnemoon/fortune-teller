import functools
import time
import os
import requests
import logging
from dataclasses import dataclass, field

from core.broker.broker import Broker, ChartCombinations
from core.broker.alphavantage.serializers import AlphaVantageLineChartDataFrameSerializer
from core.chart import LineChart
from core.interval import Interval

from core.utils.serializer import MappingSerializer

logger = logging.getLogger(__name__)

chart_dataframe_serializer = AlphaVantageLineChartDataFrameSerializer()
chart_interval_serializer = MappingSerializer({
	Interval.Day(1): 'daily',
	Interval.Week(1): 'weekly',
	Interval.Month(1): 'monthly',
	Interval.Quarter(1): 'quarterly',
	Interval.Month(6) : 'semiannual',
	Interval.Year(1): 'annual',
})
chart_maturity_serializer = MappingSerializer({
	Interval.Month(3): '3month',
	Interval.Year(2): '2year',
	Interval.Year(5): '5year',
	Interval.Year(7): '7year',
	Interval.Year(10): '10year',
	Interval.Year(30): '30year',
})

@dataclass
class AlphaVantageBroker(Broker):
	api_key: str = field(default_factory=lambda: os.getenv('ALPHAVANTAGE_API_KEY'))

	@classmethod
	@functools.cache
	def get_available_chart_combinations(self) -> ChartCombinations:
		return {
			LineChart: [
				{
					'symbol': [ 'REAL_GDP' ],
					'interval': [ Interval.Year(1), Interval.Quarter(1) ]
				},
				{
					'symbol': [ 'REAL_GDP_PER_CAPITA' ],
					'interval' : [ Interval.Quarter(1) ]
				},
				{
					'symbol': [ 'TREASURY_YIELD' ],
					'interval': [ Interval.Day(1), Interval.Week(1), Interval.Month(1) ],
					'maturity': [ Interval.Month(3), Interval.Year(2), Interval.Year(5), Interval.Year(7), Interval.Year(10), Interval.Year(30) ]
				},
				{
					'symbol': [ 'FEDERAL_FUNDS_RATE' ],
					'interval': [ Interval.Day(1), Interval.Week(1), Interval.Month(1) ]
				},
				{
					'symbol': [ 'CPI' ],
					'interval': [ Interval.Month(1), Interval.Month(6) ]
				},
				{
					'symbol': [ 'INFLATION' ],
					'interval': [ Interval.Year(1) ]
				},
				{
					'symbol': [ 'INFLATION_EXPECTATION' ],
					'interval': [ Interval.Month(1) ]
				},
				{
					'symbol': [ 'CONSUMER_SENTIMENT' ],
					'interval': [ Interval.Month(1) ]
				},
				{
					'symbol': [ 'RETAIL_SALES' ],
					'interval': [ Interval.Month(1) ]
				},
				{
					'symbol': [ 'DURABLES' ],
					'interval': [ Interval.Month(1) ]
				},
				{
					'symbol': [ 'UNEMPLOYMENT' ],
					'interval': [ Interval.Month(1) ]
				},
				{
					'symbol': [ 'NONFARM_PAYROLL' ],
					'interval': [ Interval.Month(1) ]
				},
			]
		}

	def read_chart(self, chart: LineChart):
		params = dict(
			apikey = self.api_key,
			datatype = 'json',
			outputsize = 'full',
			function = chart.symbol,
			interval = chart_interval_serializer.serialize(chart.interval),
			maturity = chart_maturity_serializer.serialize(chart.maturity)
		)

		response = requests.get('https://www.alphavantage.co/query', params=params).json()
		# SHOULD DO: find a less naive way to know if rate limit is reached
		if 'Note' in response and response['Note'].startswith('Thank you'):
			logger.warn('Rate limit reached. Waiting for 1 minute...')
			time.sleep(60) # Alphavantage only allows 5 requests per minute
			return self.read_chart(chart)

		chart.dataframe = chart_dataframe_serializer.deserialize(response['data'])