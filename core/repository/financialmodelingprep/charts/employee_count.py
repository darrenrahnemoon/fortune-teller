import pandas
from dataclasses import dataclass, field

from core.chart.serializers import ChartRecordsSerializer
from core.chart.chart import Chart
from core.interval import Interval

@dataclass
class EmployeeCountChart(Chart):
	@dataclass
	class Record(Chart.Record):
		period: pandas.Timestamp = None
		acceptance_date: pandas.Timestamp = None
		count: float = None
		form_type: str = None

@dataclass
class EmployeeCountChartSerializer(ChartRecordsSerializer):
	chart_class: type[EmployeeCountChart] = field(default_factory = lambda : EmployeeCountChart)

	def to_request(self, chart: EmployeeCountChart):
		return {
			'path' : f'/api/v4/historical/employee_count',
			'params' : {
				'symbol' : chart.symbol,
			}
		}

	def to_dataframe(self, records, *args, **kwargs):
		dataframe = pandas.DataFrame.from_records(records)
		dataframe = dataframe.drop([ 'symbol', 'companyName' ], axis = 1, errors = 'ignore')
		dataframe = dataframe.rename(
			columns = {
				'filingDate': 'timestamp',
				'acceptanceTime': 'acceptance_date',
				'periodOfReport': 'period',
				'formType': 'form_type',
				'employeeCount': 'count',
			}
		)
		return super().to_dataframe(dataframe, *args, **kwargs)
