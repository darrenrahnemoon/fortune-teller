import pandas

from .income_statement import IncomeStatements
from core.chart.serializers import ChartRecordsSerializer
from core.interval import Interval
from core.utils.serializer import MappingSerializer

period_serializer = MappingSerializer({
	Interval.Year(1) : 'year',
	Interval.Quarter(1) : 'quarter'
})

class IncomeStatementsSerializer(ChartRecordsSerializer):
	chart_class = IncomeStatements

	def to_request(self, chart: IncomeStatements):
		return {
			'path' : f'/api/v3/income-statement/{chart.symbol}',
			'params' : {
				'period' : period_serializer.serialize(chart.interval),
				'limit' : chart.count
			}
		}

	def to_dataframe(self, records, *args, **kwargs):
		dataframe = pandas.DataFrame.from_records(records)
		dataframe = dataframe.drop([ 'symbol', 'link', 'finalLink' ], axis = 1)
		dataframe = dataframe.rename(
			columns = {
				'date' : 'timestamp',
				'reportedCurrency' : 'reported_currency',
				'cik' : 'cik',
				'fillingDate' : 'filing_date',
				'acceptedDate' : 'accepted_date',
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
