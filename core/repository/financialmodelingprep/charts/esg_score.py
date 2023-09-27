import pandas
from dataclasses import dataclass, field

from core.chart.serializers import ChartRecordsSerializer
from core.chart.chart import Chart
from core.interval import Interval

@dataclass
class ESGScoreChart(Chart):
	@dataclass
	class Record(Chart.Record):
		accepted_date: pandas.Timestamp
		environmental_score: float
		social_score: float
		governance_score: float
		esg_score: float
		form_type: str


@dataclass
class ESGScoreChartSerializer(ChartRecordsSerializer):
	chart_class: type[ESGScoreChart] = field(default_factory = lambda : ESGScoreChart)

	def to_request(self, chart: ESGScoreChart):
		return {
			'path' : f'/api/v4/esg-environmental-social-governance-data',
			'params' : {
				'symbol' : chart.symbol,
			}
		}

	def to_dataframe(self, records, *args, **kwargs):
		dataframe = pandas.DataFrame.from_records(records)
		dataframe = dataframe.drop([ 'symbol' ], axis = 1)
		dataframe = dataframe.rename(
			columns = {
				'date' : 'timestamp',
				'acceptedDate' : 'accepted_date',
				'environmentalScore' : 'environmental_score',
				'socialScore' : 'social_score',
				'governanceScore' : 'governance_score',
				'ESGScore' : 'esg_score',
				'formType' : 'form_type',
			}
		)
		return super().to_dataframe(dataframe, *args, **kwargs)
