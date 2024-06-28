# Repository
A `Repository` is an integration to third-party financial data providers that allows for filtering, sorting financial data.

## MetaTraderRepository ([./metatrader/](./metatrader/))
Provides integration with MetaTrader5 to read chart data.

## SimulationRepository ([./simulation/](./simulation/))
Provides a mocked repository that allows reading data from the warehoused data from financial data providers instead of live data. 

## AlphaVantageRepository ([./alphavantage/](./alphavantage/))
Provides integration with the [AlphaVantage API](https://www.alphavantage.co/) to read economical indicator data.

**Note:** You must have the `ALPHAVANTAGE_API_KEY` environment variable set to the API key obtained from Alphavantage.

## FinancialModelingPrepRepository ([./financialmodelingprep/](./financialmodelingprep/))
Provides integration with the [Financial Modeling Prep API](https://site.financialmodelingprep.com/) to read fundamental data from public companies SEC filings, etc.

**Note:** You must have the `FINANCIAL_MODELING_PREP_API_KEY` environment variable set to the API key obtained from Financial Modeling Prep.