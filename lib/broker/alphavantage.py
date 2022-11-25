import pandas
import time
import os
import requests
import logging

from lib.broker.broker import Broker
from lib.chart import LineChart, Chart
from lib.interval import Interval

logger = logging.getLogger(__name__)

class AlphaVantageBroker(Broker):
	intervals = {
		Interval.Day(1): 'daily',
		Interval.Week(1): 'weekly',
		Interval.Month(1): 'monthly',
		Interval.Quarter(1): 'quarterly',
		Interval.Month(6) : 'semiannual',
		Interval.Year(1): 'annual',

		# For Maturity
		Interval.Month(3): '3month',
		Interval.Year(2): '2year',
		Interval.Year(5): '5year',
		Interval.Year(7): '7year',
		Interval.Year(10): '10year',
		Interval.Year(30): '30year',
	}

	available_data = {
		'REAL_GDP': { LineChart: { 'interval': [ Interval.Year(1), Interval.Quarter(1) ] } },
		'REAL_GDP_PER_CAPITA': { LineChart: { 'interval': [ Interval.Quarter(1) ] } },
		'TREASURY_YIELD': { 
			LineChart: {
				'interval': [ Interval.Day(1), Interval.Week(1), Interval.Month(1) ],
				'maturity': [ Interval.Month(3), Interval.Year(2), Interval.Year(5), Interval.Year(7), Interval.Year(10), Interval.Year(30) ]
			} 
		},
		'FEDERAL_FUNDS_RATE': { LineChart: { 'interval': [ Interval.Day(1), Interval.Week(1), Interval.Month(1) ] } },
		'CPI': { LineChart: { 'interval': [ Interval.Month(1), Interval.Month(6) ] } },
		'INFLATION': { LineChart: { 'interval': [ Interval.Year(1) ] } },
		'INFLATION_EXPECTATION': { LineChart: { 'interval': [ Interval.Month(1) ] } },
		'CONSUMER_SENTIMENT': { LineChart: { 'interval': [ Interval.Month(1) ] } },
		'RETAIL_SALES': { LineChart: { 'interval': [ Interval.Month(1) ] } },
		'DURABLES': { LineChart: { 'interval': [ Interval.Month(1) ] } },
		'UNEMPLOYMENT': { LineChart: { 'interval': [ Interval.Month(1) ] } },
		'NONFARM_PAYROLL': { LineChart: { 'interval': [ Interval.Month(1) ] } },
	}

	def __init__(
		self,
		apikey: str = os.getenv('ALPHAVANTAGE_API_KEY', None)
	) -> None:
		super().__init__()
		self.apikey = apikey

	def read_chart(self, chart: Chart):
		if type(chart) != LineChart:
			logger.error(f"Unsupported chart type '{chart}'...")
			return chart

		params = dict(
			apikey= self.apikey,
			datatype= 'json',
			outputsize= 'full',
			function= chart.symbol,
		)
		for key in self.available_data[chart.symbol][type(chart)]:
			value = getattr(chart, key)
			if value in self.intervals:
				value = value.to_broker(self)
			params[key] = value

		response = requests.get('https://www.alphavantage.co/query', params=params).json()
		# SHOULD DO: find a less naive way to know if rate limit is reached
		if 'Note' in response and response['Note'].startswith('Thank you'):
			logger.warn('Rate limit reached. Waiting for 1 minute...')
			time.sleep(60) # Alphavantage only allows 5 requests per minute
			return self.read_chart(chart)

		data = response['data']
		dataframe = pandas.DataFrame.from_records(data, index='date')

		# Value-related transformations
		dataframe = dataframe[dataframe['value'] != '.']
		dataframe['value'] = dataframe['value'].astype(float)

		# Timestamp-related transformations
		dataframe.index = pandas.to_datetime(dataframe.index)
		dataframe.index.name = 'timestamp'
		dataframe = dataframe.reindex(index=dataframe.index[::-1])

		chart.load_dataframe(dataframe)