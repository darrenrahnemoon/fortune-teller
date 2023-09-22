from .charts import IncomeStatements
from .charts.serializers import IncomeStatementsSerializer

class FinancialModelingPrepSerializers:
	records = {
		IncomeStatements : IncomeStatementsSerializer()
	}