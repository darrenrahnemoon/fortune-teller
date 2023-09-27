import pandas
from dataclasses import dataclass, field

from core.utils.serializer import MappingSerializer
from core.chart.serializers import ChartRecordsSerializer
from core.chart.chart import Chart
from core.interval import Interval

@dataclass
class BalanceSheetChart(Chart):
	interval: Interval = field(default_factory = lambda : Interval.Year(1))

	@dataclass
	class Query(Chart.Query):
		interval: Interval = None

	@dataclass
	class Record(Chart.Record):
		reported_currency: str = None
		filling_date: pandas.Timestamp = None
		accepted_date: pandas.Timestamp = None
		calendar_year: int = None
		period: str = None
		cash_and_cash_equivalents: float = None
		short_term_investments: float = None
		cash_and_short_term_investments: float = None
		net_receivables: float = None
		inventory: float = None
		other_current_assets: float = None
		total_current_assets: float = None
		property_plant_equipment_net: float = None
		goodwill: float = None
		intangible_assets: float = None
		goodwill_and_intangible_assets: float = None
		long_term_investments: float = None
		tax_assets: float = None
		other_non_current_assets: float = None
		total_non_current_assets: float = None
		other_assets: float = None
		total_assets: float = None
		account_payables: float = None
		short_term_debt: float = None
		tax_payables: float = None
		deferred_revenue: float = None
		other_current_liabilities: float = None
		total_current_liabilities: float = None
		long_term_debt: float = None
		deferred_revenue_non_current: float = None
		deferred_tax_liabilities_non_current: float = None
		other_non_current_liabilities: float = None
		total_non_current_liabilities: float = None
		other_liabilities: float = None
		capital_lease_obligations: float = None
		total_liabilities: float = None
		preferred_stock: float = None
		common_stock: float = None
		retained_earnings: float = None
		accumulated_other_comprehensive_income_loss: float = None
		other_total_stockholders_equity: float = None
		total_stockholders_equity: float = None
		total_equity: float = None
		totalLiabilitiesAnd_stockholders_equity: float = None
		minority_interest: float = None
		total_liabilities_and_total_equity: float = None
		total_investments: float = None
		total_debt: float = None
		net_debt: float = None


period_serializer = MappingSerializer({
	Interval.Year(1) : 'year',
	Interval.Quarter(1) : 'quarter'
})

@dataclass
class BalanceSheetChartSerializer(ChartRecordsSerializer):
	chart_class: type[BalanceSheetChart] = field(default_factory = lambda : BalanceSheetChart)

	def to_request(self, chart: BalanceSheetChart):
		return {
			'path' : f'/api/v3/balance-sheet-statement/{chart.symbol}',
			'params' : {
				'period' : period_serializer.serialize(chart.interval),
				'limit' : chart.count,
			}
		}

	def to_dataframe(self, records, *args, **kwargs):
		dataframe = pandas.DataFrame.from_records(records)
		dataframe = dataframe.drop([ 'symbol', 'cik', 'link', 'finalLink' ], axis = 1)
		dataframe = dataframe.rename(
			columns = {
				'date' : 'timestamp',
				'reportedCurrency' : 'reported_currency',
				'fillingDate' : 'filling_date',
				'acceptedDate' : 'accepted_date',
				'calendarYear' : 'calendar_year',
				'period' : 'period',
				'cashAndCashEquivalents' : 'cash_and_cash_equivalents',
				'shortTermInvestments' : 'short_term_investments',
				'cashAndShortTermInvestments' : 'cash_and_short_term_investments',
				'netReceivables' : 'net_receivables',
				'inventory' : 'inventory',
				'otherCurrentAssets' : 'other_current_assets',
				'totalCurrentAssets' : 'total_current_assets',
				'propertyPlantEquipmentNet' : 'property_plant_equipment_net',
				'goodwill' : 'goodwill',
				'intangibleAssets' : 'intangible_assets',
				'goodwillAndIntangibleAssets' : 'goodwill_and_intangible_assets',
				'longTermInvestments' : 'long_term_investments',
				'taxAssets' : 'tax_assets',
				'otherNonCurrentAssets' : 'other_non_current_assets',
				'totalNonCurrentAssets' : 'total_non_current_assets',
				'otherAssets' : 'other_assets',
				'totalAssets' : 'total_assets',
				'accountPayables' : 'account_payables',
				'shortTermDebt' : 'short_term_debt',
				'taxPayables' : 'tax_payables',
				'deferredRevenue' : 'deferred_revenue',
				'otherCurrentLiabilities' : 'other_current_liabilities',
				'totalCurrentLiabilities' : 'total_current_liabilities',
				'longTermDebt' : 'long_term_debt',
				'deferredRevenueNonCurrent' : 'deferred_revenue_non_current',
				'deferredTaxLiabilitiesNonCurrent' : 'deferred_tax_liabilities_non_current',
				'otherNonCurrentLiabilities' : 'other_non_current_liabilities',
				'totalNonCurrentLiabilities' : 'total_non_current_liabilities',
				'otherLiabilities' : 'other_liabilities',
				'capitalLeaseObligations' : 'capital_lease_obligations',
				'totalLiabilities' : 'total_liabilities',
				'preferredStock' : 'preferred_stock',
				'commonStock' : 'common_stock',
				'retainedEarnings' : 'retained_earnings',
				'accumulatedOtherComprehensiveIncomeLoss' : 'accumulated_other_comprehensive_income_loss',
				'othertotalStockholdersEquity' : 'other_total_stockholders_equity',
				'totalStockholdersEquity' : 'total_stockholders_equity',
				'totalEquity' : 'total_equity',
				'totalLiabilitiesAndStockholdersEquity' : 'totalLiabilitiesAnd_stockholders_equity',
				'minorityInterest' : 'minority_interest',
				'totalLiabilitiesAndTotalEquity' : 'total_liabilities_and_total_equity',
				'totalInvestments' : 'total_investments',
				'totalDebt' : 'total_debt',
				'netDebt' : 'net_debt',
			}
		)
		return super().to_dataframe(dataframe, *args, **kwargs)
