import pandas
from dataclasses import dataclass, field

from core.utils.serializer import MappingSerializer
from core.chart.serializers import ChartRecordsSerializer
from core.chart.chart import Chart
from core.interval import Interval

@dataclass
class IncomeStatementChart(Chart):
	interval: Interval = field(default_factory = lambda : Interval.Year(1))

	@dataclass
	class Query(Chart.Query):
		interval: Interval = None

	@dataclass
	class Record(Chart.Record):
		reported_currency: str = None
		filing_date: pandas.Timestamp = None
		calendar_year: pandas.Timestamp = None
		period: str = None
		revenue: float = None
		cost_of_revenue: float = None
		gross_profit: float = None
		gross_profit_ratio: float = None
		research_and_development_expenses: float = None
		general_and_administrative_expenses: float = None
		selling_and_marketing_expenses: float = None
		selling_general_and_administrative_expenses: float = None
		other_expenses: float = None
		operating_expenses: float = None
		cost_and_expenses: float = None
		interest_income: float = None
		interest_expense: float = None
		depreciation_and_amortization: float = None
		earnings_before_interest_taxes_depreciation_and_amortization: float = None
		earnings_before_interest_taxes_depreciation_and_amortization_ratio: float = None
		operating_income: float = None
		operating_income_ratio: float = None
		total_other_income_expenses_net: float = None
		income_before_tax: float = None
		income_before_tax_ratio: float = None
		income_tax_expense: float = None
		net_income: float = None
		net_income_ratio: float = None
		earnings_per_share: float = None
		earnings_per_share_diluted: float = None
		weighted_average_shares_outstanding: float = None
		weighted_average_shares_outstanding_diluted: float = None


period_serializer = MappingSerializer({
	Interval.Year(1) : 'year',
	Interval.Quarter(1) : 'quarter'
})

@dataclass
class IncomeStatementChartSerializer(ChartRecordsSerializer):
	chart_class: type[IncomeStatementChart] = field(default_factory = lambda : IncomeStatementChart)

	def to_request(self, chart: IncomeStatementChart):
		return {
			'path' : f'/api/v3/income-statement/{chart.symbol}',
			'params' : {
				'period' : period_serializer.serialize(chart.interval),
				'limit' : chart.count
			}
		}

	def to_dataframe(self, records, *args, **kwargs):
		dataframe = pandas.DataFrame.from_records(records)
		dataframe = dataframe.drop([ 'symbol', 'cik', 'link', 'finalLink', 'date' ], axis = 1)
		dataframe = dataframe.rename(
			columns = {
				'acceptedDate' : 'timestamp',
				'reportedCurrency' : 'reported_currency',
				'fillingDate' : 'filing_date',
				'calendarYear' : 'calendar_year',
				'period' : 'period',
				'revenue' : 'revenue',
				'costOfRevenue' : 'cost_of_revenue',
				'grossProfit' : 'gross_profit',
				'grossProfitRatio' : 'gross_profit_ratio',
				'researchAndDevelopmentExpenses' : 'research_and_development_expenses',
				'generalAndAdministrativeExpenses' : 'general_and_administration_expenses',
				'sellingAndMarketingExpenses' : 'selling_and_marketing_expenses',
				'sellingGeneralAndAdministrativeExpenses' : 'selling_general_and_administration_expenses',
				'otherExpenses' : 'other_expenses',
				'operatingExpenses' : 'operating_expenses',
				'costAndExpenses' : 'cost_and_expenses',
				'interestIncome' : 'interest_income',
				'interestExpense' : 'interest_expense',
				'depreciationAndAmortization' : 'depreciation_and_amortization',
				'ebitda' : 'earnings_before_interest_taxes_depreciation_and_amortization',
				'ebitdaratio' : 'earnings_before_interest_taxes_depreciation_and_amortization_ratio',
				'operatingIncome' : 'operating_income',
				'operatingIncomeRatio' : 'operating_income_ratio',
				'totalOtherIncomeExpensesNet' : 'total_other_income_expenses_net',
				'incomeBeforeTax' : 'income_before_tax',
				'incomeBeforeTaxRatio' : 'income_before_tax_ratio',
				'incomeTaxExpense' : 'income_tax_expense',
				'netIncome' : 'net_income',
				'netIncomeRatio' : 'net_income_ratio',
				'eps' : 'earnings_per_share',
				'epsdiluted' : 'earnings_per_share_diluted',
				'weightedAverageShsOut' : 'weighted_average_shares_outstanding',
				'weightedAverageShsOutDil' : 'weighted_average_shares_outstanding_diluted',
			}
		)
		return super().to_dataframe(dataframe, *args, **kwargs)
