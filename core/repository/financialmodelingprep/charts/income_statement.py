import pandas
from dataclasses import dataclass

from core.chart.chart import Chart
from core.interval import Interval

@dataclass
class IncomeStatements(Chart):
	interval: Interval = None

	@dataclass
	class Query(Chart.Query):
		interval: Interval = None

	@dataclass
	class Record(Chart.Record):
		reported_currency: str = None
		cik: float = None
		filing_date: pandas.Timestamp = None
		accepted_date: pandas.Timestamp = None
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