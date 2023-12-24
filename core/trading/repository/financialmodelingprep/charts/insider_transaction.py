import pandas
from dataclasses import dataclass, field

from core.trading.chart.serializers import ChartRecordsSerializer
from core.trading.chart.chart import Chart

@dataclass
class InsiderTransactionChart(Chart):
	@dataclass
	class Record(Chart.Record):
		transaction_date: pandas.Timestamp = None
		report_cik: str = None
		insider_name: str = None
		insider_type: str = None
		insider_securities_owned: float = None
		transaction_type: str = None
		transaction_security_name: str = None
		transaction_security_count: float = None
		transaction_security_price: float = None
		transaction_acquisition_or_disposition: str = None
		form_type: str = None

@dataclass
class InsiderTransactionChartSerializer(ChartRecordsSerializer):
	chart_class: type[InsiderTransactionChart] = field(default_factory = lambda : InsiderTransactionChart)

	def to_request(self, chart: InsiderTransactionChart):
		return {
			'path' : f'/api/v4/insider-trading',
			'params' : {
				'symbol' : chart.symbol,
				'limit' : chart.count,
				'page' : None
			}
		}

	def to_dataframe(self, records, *args, **kwargs):
		dataframe = pandas.DataFrame.from_records(records)
		dataframe = dataframe.drop([ 'symbol', 'companyCik' ], axis = 1)
		dataframe = dataframe.rename(
			columns = {
				'filingDate' : 'timestamp',
				'reportingCik' : 'report_cik',
				'companyCik' : 'company_cik',
				'reportingName' : 'insider_name',
				'typeOfOwner' : 'insider_type',
				'securitiesOwned' : 'insider_securities_owned',
				'transactionDate' : 'transaction_date',
				'transactionType' : 'transaction_type',
				'securityName' : 'transaction_security_name',
				'securitiesTransacted' : 'transaction_security_count',
				'price' : 'transaction_security_price',
				'acquistionOrDisposition' : 'transaction_acquisition_or_disposition',
				'formType' : 'form_type',
			}
		)
		return super().to_dataframe(dataframe, *args, **kwargs)
