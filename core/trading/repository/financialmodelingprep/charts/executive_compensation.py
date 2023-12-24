import pandas
from dataclasses import dataclass, field

from core.trading.chart.serializers import ChartRecordsSerializer
from core.trading.chart.chart import Chart
from core.trading.interval import Interval

@dataclass
class ExecutiveCompensationChart(Chart):
	@dataclass
	class Record(Chart.Record):
		accepted_date: pandas.Timestamp = None
		name: str = None
		year: int = None
		salary: float = None
		bonus: float = None
		stock_award: float = None
		incentive_plan: float = None
		other: float = None
		total: float = None


@dataclass
class ExecutiveCompensationChartSerializer(ChartRecordsSerializer):
	chart_class: type[ExecutiveCompensationChart] = field(default_factory = lambda : ExecutiveCompensationChart)

	def to_request(self, chart: ExecutiveCompensationChart):
		return {
			'path' : f'/api/v4/governance/executive_compensation',
			'params' : {
				'symbol' : chart.symbol,
			}
		}

	def to_dataframe(self, records, *args, **kwargs):
		dataframe = pandas.DataFrame.from_records(records)
		if len(dataframe):
			dataframe = dataframe.drop([ 'symbol' ], axis = 1)
			dataframe = dataframe.rename(
				columns = {
					'filingDate': 'timestamp',
					'acceptedDate': 'accepted_date',
					'nameAndPosition': 'name',
					'year': 'year',
					'salary': 'salary',
					'bonus': 'bonus',
					'stock_award': 'stock_award',
					'incentive_plan_compensation': 'incentive_plan',
					'all_other_compensation': 'other',
					'total': 'total',
				}
			)
		return super().to_dataframe(dataframe, *args, **kwargs)
