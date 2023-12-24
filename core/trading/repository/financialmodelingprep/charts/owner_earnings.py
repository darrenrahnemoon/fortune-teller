import pandas
from dataclasses import dataclass, field

from core.trading.chart.serializers import ChartRecordsSerializer
from core.trading.chart.chart import Chart

@dataclass
class OwnerEarningsChart(Chart):
	@dataclass
	class Record(Chart.Record):
		average_property_plant_equipment: float = None
		maintenance_capital_expenditure: float = None
		growth_capital_expenditure: float = None
		owners_earnings: float = None
		owners_earnings_per_share: float = None

@dataclass
class OwnerEarningsChartSerializer(ChartRecordsSerializer):
	chart_class: type[OwnerEarningsChart] = field(default_factory = lambda : OwnerEarningsChart)

	def to_request(self, chart: OwnerEarningsChart):
		return {
			'path' : f'/api/v4/owner_earnings',
			'params' : {
				'symbol' : chart.symbol,
			}
		}

	def to_dataframe(self, records, *args, **kwargs):
		dataframe = pandas.DataFrame.from_records(records)
		dataframe = dataframe.drop([ 'symbol' ], axis = 1, errors = 'ignore')
		dataframe = dataframe.rename(
			columns = {
				'date' : 'timestamp',
				"averagePPE" : 'average_property_plant_equipment',
				"maintenanceCapex" : 'maintenance_capital_expenditure',
				"growthCapex" : 'growth_capital_expenditure',
				"ownersEarnings" : 'owners_earnings',
				"ownersEarningsPerShare" : 'owners_earnings_per_share',
			}
		)
		return super().to_dataframe(dataframe, *args, **kwargs)
