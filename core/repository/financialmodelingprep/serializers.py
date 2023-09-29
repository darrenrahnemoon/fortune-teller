from .charts.income_statement import IncomeStatementChart, IncomeStatementChartSerializer
from .charts.balance_sheet import BalanceSheetChart, BalanceSheetChartSerializer
from .charts.cash_flow_statement import CashFlowStatementChart, CashFlowStatementChartSerializer
from .charts.insider_transaction import InsiderTransactionChart, InsiderTransactionChartSerializer
from .charts.financial_ratio import FinancialRatioChart, FinancialRatioChartSerializer
from .charts.enterprise_value import EnterpriseValueChart, EnterpriseValueChartSerializer
from .charts.esg_score import ESGScoreChart, ESGScoreChartSerializer
from .charts.employee_count import EmployeeCountChart, EmployeeCountChartSerializer
from .charts.executive_compensation import ExecutiveCompensationChart, ExecutiveCompensationChartSerializer
from .charts.senate_disclosure import SenateDisclosureChart, SenateDisclosureChartSerializer
from .charts.candlestick import CandleStickChart, CandleStickChartSerializer

class FinancialModelingPrepSerializers:
	records = {
		IncomeStatementChart : IncomeStatementChartSerializer(),
		BalanceSheetChart : BalanceSheetChartSerializer(),
		CashFlowStatementChart : CashFlowStatementChartSerializer(),
		InsiderTransactionChart : InsiderTransactionChartSerializer(),
		FinancialRatioChart : FinancialRatioChartSerializer(),
		EnterpriseValueChart : EnterpriseValueChartSerializer(),
		ESGScoreChart : ESGScoreChartSerializer(),
		EmployeeCountChart : EmployeeCountChartSerializer(),
		ExecutiveCompensationChart : ExecutiveCompensationChartSerializer(),
		SenateDisclosureChart : SenateDisclosureChartSerializer(),
		CandleStickChart : CandleStickChartSerializer()
	}