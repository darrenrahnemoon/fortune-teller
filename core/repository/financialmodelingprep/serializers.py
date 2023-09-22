from .charts import IncomeStatementChart
from .charts.serializers import IncomeStatementChartSerializer

class FinancialModelingPrepSerializers:
	records = {
		IncomeStatementChart : IncomeStatementChartSerializer()
	}