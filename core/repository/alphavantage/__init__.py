import functools
import time
import os
import pandas
import requests
from dataclasses import dataclass, field

from core.repository.repository import Repository, ChartCombinations
from core.chart import LineChart, ChartParams
from core.interval import Interval
from .serializers import AlphaVantageSerializers
from core.utils.logging import logging

logger = logging.getLogger(__name__)

@dataclass
class AlphaVantageRepository(Repository):
	api_key: str = field(default = os.getenv('ALPHAVANTAGE_API_KEY'))
	serializers = AlphaVantageSerializers()

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

	def read_chart(
		self,
		chart: LineChart or ChartParams = None,
		**overrides
	) -> pandas.DataFrame:
		chart_params = ChartParams(chart, overrides)

		api_params = dict(
			apikey = self.api_key,
			datatype = 'json',
			outputsize = 'full',
			function = chart_params['symbol'],
			interval = self.serializers.interval.serialize(chart_params['interval']),
			maturity = self.serializers.treasury_yield_maturity.serialize(chart_params['maturity'])
		)

		response = requests.get('https://www.alphavantage.co/query', params = api_params).json()
		# HACK/SHOULD DO: find a less naive way to know if rate limit is reached (probably from status code)
		if 'Note' in response and response['Note'].startswith('Thank you'):
			logger.warn('Rate limit reached. Waiting for 1 minute...')
			time.sleep(60) # Alphavantage only allows 5 requests per minute
			return self.read_chart(chart, **overrides)

		return self.serializers.records.to_dataframe(
			response['data'],
			name = chart_params['name'],
			select = chart_params['select'],
			tz = self.timezone,
		)