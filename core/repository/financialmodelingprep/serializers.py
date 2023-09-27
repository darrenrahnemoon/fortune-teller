from .charts.income_statement import IncomeStatementChart, IncomeStatementChartSerializer
from .charts.balance_sheet import BalanceSheetChart, BalanceSheetChartSerializer
from .charts.cash_flow_statement import CashFlowStatementChart, CashFlowStatementChartSerializer
from .charts.insider_transaction import InsiderTransactionChart, InsiderTransactionChartSerializer
from .charts.financial_ratio import FinancialRatioChart, FinancialRatioChartSerializer
from .charts.enterprise_value import EnterpriseValueChart, EnterpriseValueChartSerializer
from .charts.esg_score import ESGScoreChart, ESGScoreChartSerializer
from .charts.employee_count import EmployeeCountChart, EmployeeCountChartSerializer

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
	}