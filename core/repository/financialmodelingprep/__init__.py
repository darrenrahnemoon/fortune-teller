import os
import pandas
import requests
from dataclasses import dataclass, field
from functools import cache

from core.repository.repository import Repository
from core.utils.cls import product_dict
from core.utils.logging import Logger
from .serializers import FinancialModelingPrepSerializers
from core.interval import Interval
from core.chart import Chart, OverriddenChart
from .charts import (
	IncomeStatementChart,
	BalanceSheetChart,
	CashFlowStatementChart,
	InsiderTransactionChart,
	FinancialRatioChart,
	EnterpriseValueChart,
	OwnerEarningsChart,
	ESGScoreChart,
	EmployeeCountChart,
	ExecutiveCompensationChart,
	SenateDisclosureChart,
	CandleStickChart
)

logger = Logger(__name__)

@dataclass
class FinancialModelingPrepRepository(Repository):
	base_url: str = 'https://financialmodelingprep.com'
	api_key: str = field(default = os.getenv('FINANCIAL_MODELING_PREP_API_KEY'))
	serializers = FinancialModelingPrepSerializers

	def read_chart(
		self,
		chart: Chart = None,
		**overrides
	) -> pandas.DataFrame:
		chart = OverriddenChart(chart, overrides)

		request = self.serializers.records[chart.type].to_request(chart)
		records = []

		page = 0
		while True:
			# Skip if endpoint doesn't support pagination and already fetched 1 page 
			if page == 1 and 'page' not in request['params']:
				break

			params = request['params'].copy()
			params['apikey'] = self.api_key
			params['page'] = page

			response = requests.get(
				self.base_url + request['path'],
				params = params,
			)
			data = response.json()
			if len(data) == 0:
				break

			records.extend(data)
			page += 1

		return self.serializers.records[chart.type].to_dataframe(
			records,
			name = chart.name,
			select = chart.select,
			tz = self.timezone,
		)

	def get_charts(self, **kwargs):
		symbols = self.get_available_symbols()
		combinations = [
			{
				'type' : [ IncomeStatementChart ],
				'symbol': symbols,
				'interval': [ Interval.Year(1), Interval.Quarter(1) ]
			},
			{
				'type' : [ BalanceSheetChart ],
				'symbol': symbols,
				'interval': [ Interval.Year(1), Interval.Quarter(1) ]
			},
			{
				'type' : [ CashFlowStatementChart ],
				'symbol': symbols,
				'interval': [ Interval.Year(1), Interval.Quarter(1) ]
			},
			{
				'type' : [ InsiderTransactionChart ],
				'symbol': symbols,
			},
			{
				'type' : [ FinancialRatioChart ],
				'symbol': symbols,
				'interval': [ Interval.Year(1), Interval.Quarter(1) ]
			},
			{
				'type' : [ EnterpriseValueChart ],
				'symbol': symbols,
				'interval': [ Interval.Year(1), Interval.Quarter(1) ]
			},
			{
				'type' : [ OwnerEarningsChart ],
				'symbol': symbols,
			},
			{
				'type' : [ ESGScoreChart ],
				'symbol': symbols,
			},
			{
				'type' : [ EmployeeCountChart ],
				'symbol': symbols,
			},
			{
				'type' : [ SenateDisclosureChart ],
				'symbol': symbols,
			},
			{
				'type' : [ ExecutiveCompensationChart ],
				'symbol': symbols,
			},
			{
				'type' : [ CandleStickChart ],
				'symbol': symbols,
				'interval' : [ Interval.Minute(1), Interval.Minute(5), Interval.Minute(15), Interval.Minute(30), Interval.Hour(1), Interval.Hour(4) ],
			},
		]
		for combination in combinations:
			for chart_params in product_dict(combination):
				yield chart_params.pop('type')(**chart_params)

	def get_available_symbols(self):
		response = requests.get(
			f'{self.base_url}/api/v3/financial-statement-symbol-lists',
			params = {
				'apikey': self.api_key
			}
		)
		symbols = response.json()

		return symbols