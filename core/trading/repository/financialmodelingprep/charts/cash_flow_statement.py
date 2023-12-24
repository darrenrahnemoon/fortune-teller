import pandas
from dataclasses import dataclass, field

from core.utils.serializer import MappingSerializer
from core.trading.chart.serializers import ChartRecordsSerializer
from core.trading.chart.chart import Chart
from core.trading.interval import Interval

@dataclass
class CashFlowStatementChart(Chart):
	interval: Interval = field(default_factory = lambda : Interval.Year(1))

	@dataclass
	class Query(Chart.Query):
		interval: Interval = None

	@dataclass
	class Record(Chart.Record):
		reported_currency: str = None
		filling_date: pandas.Timestamp = None
		calendar_year: int = None
		period: str = None
		net_income: float = None
		depreciation_and_amortization: float = None
		deferred_income_tax: float = None
		stock_based_compensation: float = None
		change_in_working_capital: float = None
		accounts_receivables: float = None
		inventory: float = None
		accounts_payables: float = None
		other_working_capital: float = None
		other_non_cash_items: float = None
		net_cash_provided_by_operating_activities: float = None
		investments_in_property_plant_and_equipment: float = None
		acquisitions_net: float = None
		purchases_of_investments: float = None
		sales_maturities_of_investments: float = None
		other_investing_activities: float = None
		net_cash_used_for_investing_activities: float = None
		debt_repayment: float = None
		common_stock_issued: float = None
		common_stock_repurchased: float = None
		dividends_paid: float = None
		other_financing_activities: float = None
		net_cash_used_provided_by_financing_activities: float = None
		effect_of_forex_changes_on_cash: float = None
		net_change_in_cash: float = None
		cash_at_end_of_period: float = None
		cash_at_beginning_of_period: float = None
		operating_cash_flow: float = None
		capital_expenditure: float = None
		free_cash_flow: float = None


period_serializer = MappingSerializer({
	Interval.Year(1) : 'year',
	Interval.Quarter(1) : 'quarter'
})

@dataclass
class CashFlowStatementChartSerializer(ChartRecordsSerializer):
	chart_class: type[CashFlowStatementChart] = field(default_factory = lambda : CashFlowStatementChart)

	def to_request(self, chart: CashFlowStatementChart):
		return {
			'path' : f'/api/v3/balance-sheet-statement/{chart.symbol}',
			'params' : {
				'period' : period_serializer.serialize(chart.interval),
				'limit' : chart.count,
			}
		}

	def to_dataframe(self, records, *args, **kwargs):
		dataframe = pandas.DataFrame.from_records(records)
		dataframe = dataframe.drop([ 'symbol', 'cik', 'link', 'finalLink', 'date' ], axis = 1)
		dataframe = dataframe.rename(
			columns = {
				'acceptedDate' : 'timestamp',
				'filingDate' : 'filing_date',
				'reportedCurrency' : 'reported_currency',
				'calendarYear' : 'calendar_year',
				'period' : 'period',
				'netIncome' : 'net_income',
				'depreciationAndAmortization' : 'depreciation_and_amortization',
				'deferredIncomeTax' : 'deferred_income_tax',
				'stockBasedCompensation' : 'stock_based_compensation',
				'changeInWorkingCapital' : 'change_in_working_capital',
				'accountsReceivables' : 'accounts_receivables',
				'inventory' : 'inventory',
				'accountsPayables' : 'accounts_payables',
				'otherWorkingCapital' : 'other_working_capital',
				'otherNonCashItems' : 'other_non_cash_items',
				'netCashProvidedByOperatingActivities' : 'net_cash_provided_by_operating_activities',
				'investmentsInPropertyPlantAndEquipment' : 'investments_in_property_plant_and_equipment',
				'acquisitionsNet' : 'acquisitions_net',
				'purchasesOfInvestments' : 'purchases_of_investments',
				'salesMaturitiesOfInvestments' : 'sales_maturities_of_investments',
				'otherInvestingActivites' : 'other_investing_activities',
				'netCashUsedForInvestingActivites' : 'net_cash_used_for_investing_activities',
				'debtRepayment' : 'debt_repayment',
				'commonStockIssued' : 'common_stock_issued',
				'commonStockRepurchased' : 'common_stock_repurchased',
				'dividendsPaid' : 'dividends_paid',
				'otherFinancingActivites' : 'other_financing_activities',
				'netCashUsedProvidedByFinancingActivities' : 'net_cash_used_provided_by_financing_activities',
				'effectOfForexChangesOnCash' : 'effect_of_forex_changes_on_cash',
				'netChangeInCash' : 'net_change_in_cash',
				'cashAtEndOfPeriod' : 'cash_at_end_of_period',
				'cashAtBeginningOfPeriod' : 'cash_at_beginning_of_period',
				'operatingCashFlow' : 'operating_cash_flow',
				'capitalExpenditure' : 'capital_expenditure',
				'freeCashFlow' : 'free_cash_flow',
			}
		)
		return super().to_dataframe(dataframe, *args, **kwargs)
