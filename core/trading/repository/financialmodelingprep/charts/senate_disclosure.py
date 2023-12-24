import pandas
from dataclasses import dataclass, field

from core.trading.chart.serializers import ChartRecordsSerializer
from core.trading.chart.chart import Chart

@dataclass
class SenateDisclosureChart(Chart):
	@dataclass
	class Record(Chart.Record):
		disclosure_year: int
		disclosure_date: pandas.Timestamp
		transaction_date: pandas.Timestamp
		owner: str
		type: str
		amount_min: float
		amount_max: float
		name: str
		district: str
		state: str
		capital_gains_over_200_usd: bool

@dataclass
class SenateDisclosureChartSerializer(ChartRecordsSerializer):
	chart_class: type[SenateDisclosureChart] = field(default_factory = lambda : SenateDisclosureChart)

	def to_request(self, chart: SenateDisclosureChart):
		return {
			'path' : f'/api/v4/senate-disclosure',
			'params' : {
				'symbol' : chart.symbol,
			}
		}

	def to_dataframe(self, records, *args, **kwargs):
		dataframe = pandas.DataFrame.from_records(records)
		if len(dataframe):
			dataframe = dataframe.rename(
				columns = {
					'disclosureYear': 'disclosure_year',
					'disclosureDate': 'timestamp',
					'transactionDate': 'transaction_date',
					'representative': 'name',
					'district': 'district',
					'capitalGainsOver200USD': 'capital_gains_over_200_usd',
				}
			)

			# state
			dataframe['state'] = dataframe['district'].str[:2]

			# amount range
			amount = dataframe['amount'].str.extract(r'\$(?P<min>\d+,?\d+) - \$(?P<max>\d+,?\d+)')
			dataframe['amount_min'] = amount['min'].str.replace(',', '')
			dataframe['amount_max'] = amount['max'].str.replace(',', '')

			# capital gains over 200usd
			dataframe['capital_gains_over_200_usd'] = dataframe['capital_gains_over_200_usd'] == 'True'

			dataframe = dataframe.drop([ 'ticker', 'assetDescription', 'link', 'amount' ], axis = 1, errors = 'ignore')
		return super().to_dataframe(dataframe, *args, **kwargs)
