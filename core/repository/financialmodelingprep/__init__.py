import os
import pandas
import requests
from dataclasses import dataclass, field

from core.chart import Chart, OverriddenChart

from core.repository.repository import Repository
from .serializers import FinancialModelingPrepSerializers
from core.utils.logging import Logger

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
		response = requests.get(
			self.base_url + request['path'],
			params = dict(
				**request['params'],
				apikey = self.api_key
			)
		)

		data = response.json()

		return self.serializers.records[chart.type].to_dataframe(
			data,
			name = chart.name,
			select = chart.select,
			tz = self.timezone,
		)