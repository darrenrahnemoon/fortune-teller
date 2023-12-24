import pandas
from dataclasses import dataclass, field

from core.utils.serializer import MappingSerializer
from core.trading.chart.serializers import ChartRecordsSerializer
from core.trading.chart.chart import Chart
from core.trading.interval import Interval

@dataclass
class FinancialRatioChart(Chart):
	interval: Interval = field(default_factory = lambda : Interval.Year(1))

	@dataclass
	class Query(Chart.Query):
		interval: Interval = None

	@dataclass
	class Record(Chart.Record):
		calendar_year: int = None
		period: str = None
		current_ratio: float = None
		quick_ratio: float = None
		cash_ratio: float = None
		days_of_sales_outstanding: float = None
		days_of_inventory_outstanding: float = None
		days_of_payables_outstanding: float = None
		operating_cycle: float = None
		cash_conversion_cycle: float = None
		gross_profit_margin: float = None
		operating_profit_margin: float = None
		pretax_profit_margin: float = None
		net_profit_margin: float = None
		effective_tax_rate: float = None
		return_on_assets: float = None
		return_on_equity: float = None
		return_on_capital_employed: float = None
		net_income_per_earnings_before_taxes: float = None
		earnings_before_taxes_per_earnings_before_interest_and_taxes: float = None
		earnings_before_interest_and_taxes_per_revenue: float = None
		debt_ratio: float = None
		debt_equity_ratio: float = None
		long_term_debt_to_capitalization: float = None
		total_debt_to_capitalization: float = None
		interest_coverage: float = None
		cash_flow_to_debt_ratio: float = None
		company_equity_multiplier: float = None
		receivables_turnover: float = None
		payables_turnover: float = None
		inventory_turnover: float = None
		fixed_asset_turnover: float = None
		asset_turnover: float = None
		operating_cash_flow_per_share: float = None
		free_cash_flow_per_share: float = None
		cash_per_share: float = None
		payout_ratio: float = None
		operating_cash_flow_sales_ratio: float = None
		free_cash_flow_operating_cash_flow_ratio: float = None
		cash_flow_coverage_ratios: float = None
		short_term_coverage_ratios: float = None
		capital_expenditure_coverage_ratio: float = None
		dividend_paid_and_capital_expenditure_coverage_ratio: float = None
		dividend_payout_ratio: float = None
		price_book_value_ratio: float = None
		price_to_book_ratio: float = None
		price_to_sales_ratio: float = None
		price_earnings_ratio: float = None
		price_to_free_cash_flows_ratio: float = None
		price_to_operating_cash_flows_ratio: float = None
		price_cash_flow_ratio: float = None
		price_earnings_to_growth_ratio: float = None
		price_sales_ratio: float = None
		dividend_yield: float = None
		enterprise_value_multiple: float = None
		price_fair_value: float = None


period_serializer = MappingSerializer({
	Interval.Year(1) : 'year',
	Interval.Quarter(1) : 'quarter'
})

@dataclass
class FinancialRatioChartSerializer(ChartRecordsSerializer):
	chart_class: type[FinancialRatioChart] = field(default_factory = lambda : FinancialRatioChart)

	def to_request(self, chart: FinancialRatioChart):
		return {
			'path' : f'/api/v3/ratios/{chart.symbol}',
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
				'calendarYear' : 'calendar_year',
				'period' : 'period',
				'currentRatio' : 'current_ratio',
				'quickRatio' : 'quick_ratio',
				'cashRatio' : 'cash_ratio',
				'daysOfSalesOutstanding' : 'days_of_sales_outstanding',
				'daysOfInventoryOutstanding' : 'days_of_inventory_outstanding',
				'operatingCycle' : 'operating_cycle',
				'daysOfPayablesOutstanding' : 'days_of_payables_outstanding',
				'cashConversionCycle' : 'cash_conversion_cycle',
				'grossProfitMargin' : 'gross_profit_margin',
				'operatingProfitMargin' : 'operating_profit_margin',
				'pretaxProfitMargin' : 'pretax_profit_margin',
				'netProfitMargin' : 'net_profit_margin',
				'effectiveTaxRate' : 'effective_tax_rate',
				'returnOnAssets' : 'return_on_assets',
				'returnOnEquity' : 'return_on_equity',
				'returnOnCapitalEmployed' : 'return_on_capital_employed',
				'netIncomePerEBT' : 'net_income_per_earnings_before_taxes',
				'ebtPerEbit' : 'earnings_before_taxes_per_earnings_before_interest_and_taxes',
				'ebitPerRevenue' : 'earnings_before_interest_and_taxes_per_revenue',
				'debtRatio' : 'debt_ratio',
				'debtEquityRatio' : 'debt_equity_ratio',
				'longTermDebtToCapitalization' : 'long_term_debt_to_capitalization',
				'totalDebtToCapitalization' : 'total_debt_to_capitalization',
				'interestCoverage' : 'interest_coverage',
				'cashFlowToDebtRatio' : 'cash_flow_to_debt_ratio',
				'companyEquityMultiplier' : 'company_equity_multiplier',
				'receivablesTurnover' : 'receivables_turnover',
				'payablesTurnover' : 'payables_turnover',
				'inventoryTurnover' : 'inventory_turnover',
				'fixedAssetTurnover' : 'fixed_asset_turnover',
				'assetTurnover' : 'asset_turnover',
				'operatingCashFlowPerShare' : 'operating_cash_flow_per_share',
				'freeCashFlowPerShare' : 'free_cash_flow_per_share',
				'cashPerShare' : 'cash_per_share',
				'payoutRatio' : 'payout_ratio',
				'operatingCashFlowSalesRatio' : 'operating_cash_flow_sales_ratio',
				'freeCashFlowOperatingCashFlowRatio' : 'free_cash_flow_operating_cash_flow_ratio',
				'cashFlowCoverageRatios' : 'cash_flow_coverage_ratios',
				'shortTermCoverageRatios' : 'short_term_coverage_ratios',
				'capitalExpenditureCoverageRatio' : 'capital_expenditure_coverage_ratio',
				'dividendPaidAndCapexCoverageRatio' : 'dividend_paid_and_capital_expenditure_coverage_ratio',
				'dividendPayoutRatio' : 'dividend_payout_ratio',
				'priceBookValueRatio' : 'price_book_value_ratio',
				'priceToBookRatio' : 'price_to_book_ratio',
				'priceToSalesRatio' : 'price_to_sales_ratio',
				'priceEarningsRatio' : 'price_earnings_ratio',
				'priceToFreeCashFlowsRatio' : 'price_to_free_cash_flows_ratio',
				'priceToOperatingCashFlowsRatio' : 'price_to_operating_cash_flows_ratio',
				'priceCashFlowRatio' : 'price_cash_flow_ratio',
				'priceEarningsToGrowthRatio' : 'price_earnings_to_growth_ratio',
				'priceSalesRatio' : 'price_sales_ratio',
				'dividendYield' : 'dividend_yield',
				'enterpriseValueMultiple' : 'enterprise_value_multiple',
				'priceFairValue' : 'price_fair_value',
			}
		)
		return super().to_dataframe(dataframe, *args, **kwargs)

