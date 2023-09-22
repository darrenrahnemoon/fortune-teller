import time
import os
import pandas
import requests
from dataclasses import dataclass, field

from core.repository.repository import Repository
from core.chart import LineChart, OverriddenChart
from core.interval import Interval
from .serializers import AlphaVantageSerializers
from core.utils.cls import product_dict
from core.utils.logging import Logger

logger = Logger(__name__)

@dataclass
class AlphaVantageRepository(Repository):
	base_url: str = 'https://www.alphavantage.co/query'
	api_key: str = field(default = os.getenv('ALPHAVANTAGE_API_KEY'))
	serializers = AlphaVantageSerializers()

	def get_all_available_charts(self, **kwargs):
		combinations = [
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
		for combination in combinations:
			for chart_params in product_dict(combination):
				yield LineChart(**chart_params)

	def read_chart(
		self,
		chart: LineChart or OverriddenChart = None,
		**overrides
	) -> pandas.DataFrame:
		chart = OverriddenChart(chart, overrides)

		api_params = dict(
			apikey = self.api_key,
			datatype = 'json',
			outputsize = 'full',
			function = chart.symbol,
			interval = self.serializers.interval.serialize(chart.interval),
			maturity = self.serializers.treasury_yield_maturity.serialize(chart.maturity)
		)

		response = requests.get(self.base_url, params = api_params).json()
		# HACK/SHOULD DO: find a less naive way to know if rate limit is reached (probably from status code)
		if 'Note' in response and response['Note'].startswith('Thank you'):
			logger.warn('Rate limit reached. Waiting for 1 minute...')
			time.sleep(60) # Alphavantage only allows 5 requests per minute
			return self.read_chart(chart, **overrides)

		if not 'data' in response:
			raise Exception(f"Missing 'data' in response:\n{response}")

		return self.serializers.records.to_dataframe(
			response['data'],
			name = chart.name,
			select = chart.select,
			tz = self.timezone,
		)