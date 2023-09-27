import pandas
from dataclasses import dataclass, field

from core.utils.serializer import MappingSerializer
from core.chart.serializers import ChartRecordsSerializer
from core.chart.chart import Chart
from core.interval import Interval

@dataclass
class EnterpriseValueChart(Chart):
	interval: Interval = field(default_factory = lambda : Interval.Year(1))

	@dataclass
	class Query(Chart.Query):
		interval: Interval = None

	@dataclass
	class Record(Chart.Record):
		stock_price : float = None
		number_of_shares : float = None
		market_capitalization : float = None
		cash_and_cash_equivalents : float = None
		total_debt : float = None
		enterprise_value : float = None

period_serializer = MappingSerializer({
	Interval.Year(1) : 'year',
	Interval.Quarter(1) : 'quarter'
})

@dataclass
class EnterpriseValueChartSerializer(ChartRecordsSerializer):
	chart_class: type[EnterpriseValueChart] = field(default_factory = lambda : EnterpriseValueChart)

	def to_request(self, chart: EnterpriseValueChart):
		return {
			'path' : f'/api/v3/enterprise-values/{chart.symbol}',
			'params' : {
				'period' : period_serializer.serialize(chart.interval),
				'limit' : chart.count,
			}
		}

	def to_dataframe(self, records, *args, **kwargs):
		dataframe = pandas.DataFrame.from_records(records)
		dataframe = dataframe.drop([ 'symbol' ], axis = 1)
		dataframe = dataframe.rename(
			columns = {
				'date' : 'timestamp',
				'stockPrice' : 'stock_price',
				'numberOfShares' : 'number_of_shares',
				'marketCapitalization' : 'market_capitalization',
				'minusCashAndCashEquivalents' : 'cash_and_cash_equivalents',
				'addTotalDebt' : 'total_debt',
				'enterpriseValue' : 'enterprise_value',
			}
		)
		return super().to_dataframe(dataframe, *args, **kwargs)
