from core.interval import Interval
from core.indicator import SeasonalityIndicator
from core.repository import Repository, SimulationRepository, MetaTraderRepository
from core.utils.config import Config, dataclass, field, on_stage

from core.chart import ChartGroup, CandleStickChart
from core.repository.financialmodelingprep.charts import (
	IncomeStatementChart,
	BalanceSheetChart,
	CashFlowStatementChart,
	InsiderTransactionChart,
	FinancialRatioChart,
	EnterpriseValueChart,
	OwnerEarningsChart,
	ESGScoreChart,
	EmployeeCountChart,
	ExecutiveCompensationChart,
	SenateDisclosureChart
)

@dataclass
class ObservationConfig(Config):
	symbols: list[str] = field(
		default_factory = lambda: [
			'ABBV',
			'ABT',
			'AXP',
			'BA',
			'BAC',
			'BLK',
			'BMY',
			'C',
			'CVS',
			'CVX',
			'DD',
			'DIS',
			'GE',
			'GS',
			'HD',
			'HON',
			'IBM',
			'JNJ',
			'JPM',
			'KO',
			'LLY',
			'LMT',
			'MA',
			'MCD',
			'MMM',
			'MO',
			'MRK',
			'MS',
			'NKE',
			'ORCL',
			'PFE',
			'PG',
			'PM',
			'SLB',
			'T',
			'UNH',
			'UNP',
			'UPS',
			'USB',
			'V',
			'VZ',
			'WFC',
			'WMT',
			'XOM',
			'LIN',
			'NEE',
			'AMT',
			'TMO',
			'AES',
			'AFL',
			'A',
			'APD',
			'ALK',
			'ALB',
			'ARE',
			'ALLE',
			'ALL',
			'AEE',
			'AIG',
			'AWK',
			'AMP',
			'AME',
			'APH',
			'AON',
			'AOS',
			'APTV',
			'ADM',
			'ANET',
			'AJG',
			'AIZ',
			'ATO',
			'AZO',
			'AVB',
			'AVY',
			'BKR',
			'BK',
			'BAX',
			'BDX',
			'BBY',
			'BIO',
			'BWA',
			'BXP',
			'BSX',
			'BR',
			'CPB',
			'COF',
			'CAH',
			'KMX',
			'CCL',
			'CTLT',
			'CAT',
			'CBRE',
			'CE',
			'CNC',
			'CNP',
			'CF',
			'SCHW',
			'CMG',
			'CB',
			'CHD',
			'CI',
			'CFG',
			'CLX',
			'CMS',
			'CL',
			'CMA',
			'CAG',
			'COP',
			'ED',
			'STZ',
			'GLW',
			'CCI',
			'CMI',
			'DHI',
			'DHR',
			'DRI',
			'DVA',
			'DE',
			'ACN',
			'DAL',
			'DVN',
			'DLR',
			'DFS',
			'DG',
			'D',
			'DPZ',
			'DOV',
			'DTE',
			'DUK',
			'DXC',
			'EMN',
			'ETN',
			'ECL',
			'EIX',
			'EW',
			'EMR',
			'ETR',
			'EOG',
			'EFX',
			'EQR',
			'ESS',
			'EL',
			'ES',
			'EXR',
			'FRT',
			'FDX',
			'FIS',
			'FE',
			'FLT',
			'FMC',
			'F',
			'FTV',
			'FCX',
			'IT',
			'BEN',
			'GD',
			'GIS',
			'GM',
			'GL',
			'GPN',
			'GWW',
			'HAL',
			'HIG',
			'HCA',
			'PEAK',
			'HSY',
			'HES',
			'HPE',
			'HLT',
			'HRL',
			'HWM',
			'HPQ',
			'HUM',
			'HII',
			'IEX',
			'ITW',
			'IR',
			'ICE',
			'IP',
			'IPG',
			'IFF',
			'IVZ',
			'NI',
			'IQV',
			'IRM',
			'J',
			'SJM',
			'JCI',
			'JNPR',
			'K',
			'KEY',
			'KEYS',
			'KMB',
			'KIM',
			'KMI',
			'KR',
			'LHX',
			'LH',
			'LW',
			'LVS',
			'LDOS',
			'LEN',
			'LYV',
			'L',
			'LOW',
			'LYB',
			'MTB',
			'MRO',
			'MPC',
			'MMC',
			'MLM',
			'MAS',
			'MKC',
			'MCK',
			'MDT',
			'MET',
			'MTD',
			'MGM',
			'MAA',
			'MHK',
			'TAP',
			'MCO',
			'MOS',
			'MSI',
			'MSCI',
			'NEM',
			'NSC',
			'NOC',
			'NCLH',
			'NRG',
			'NUE',
			'NVR',
			'OXY',
			'OMC',
			'OKE',
			'PKG',
			'PH',
			'PAYC',
			'PNR',
			'PSX',
			'PNW',
			'PXD',
			'PNC',
			'PPG',
			'PPL',
			'PGR',
			'PLD',
			'PRU',
			'PEG',
			'PSA',
			'PHM',
			'PWR',
			'DGX',
			'RJF',
			'O',
			'RF',
			'RSG',
			'RMD',
			'RHI',
			'ROK',
			'ROL',
			'ROP',
			'RCL',
			'SPGI',
			'CRM',
			'SEE',
			'SRE',
			'NOW',
			'SPG',
			'SNA',
			'SO',
			'LUV',
			'SWK',
			'STT',
			'STE',
			'SYK',
			'SYF',
			'SYY',
			'TPR',
			'TGT',
			'TEL',
			'TDY',
			'TFX',
			'TXT',
			'TJX',
			'TT',
			'TDG',
			'TRV',
			'TFC',
			'TYL',
			'TSN',
			'UDR',
			'URI',
			'UHS',
			'VLO',
			'VTR',
			'VFC',
			'VMC',
			'WRB',
			'WAB',
			'WM',
			'WAT',
			'WEC',
			'WELL',
			'WST',
			'WRK',
			'WY',
			'WHR',
			'WMB',
			'XYL',
			'YUM',
			'ZBH',
			'RTX',
			'BX',
			'PANW',
			'PCG',
			'EPAM',
			'GNRC',
			'INVH',
			'CRL',
			'CDAY',
			'FICO',
			'MOH',
			'BRO',
			'FDS',
			'BG',
			'CPT',
			'EQT',
			'TRGP',
			'RL',
			'GRMN',
			'AAPL',
			'ADBE',
			'ADI',
			'ADP',
			'AMAT',
			'AMGN',
			'AMZN',
			'ATVI',
			'AVGO',
			'BKNG',
			'BIIB',
			'CHTR',
			'CMCSA',
			'CME',
			'COST',
			'CSCO',
			'CSX',
			'CTSH',
			'EA',
			'EBAY',
			'EQIX',
			'FOX',
			'FOXA',
			'GILD',
			'GOOG',
			'INTC',
			'INTU',
			'ISRG',
			'KHC',
			'MAR',
			'MDLZ',
			'MSFT',
			'MU',
			'NFLX',
			'NVDA',
			'PEP',
			'PYPL',
			'QCOM',
			'REGN',
			'SBUX',
			'TMUS',
			'TSLA',
			'TXN',
			'VRTX',
			'WBA',
			'AMD',
			'AKAM',
			'ALGN',
			'LNT',
			'AAL',
			'AEP',
			'ANSS',
			'APA',
			'ADSK',
			'CHRW',
			'CDNS',
			'CDW',
			'CINF',
			'CTAS',
			'CPRT',
			'XRAY',
			'DXCM',
			'FANG',
			'DLTR',
			'ENPH',
			'ETSY',
			'EXC',
			'EXPE',
			'EXPD',
			'FFIV',
			'FAST',
			'FITB',
			'FTNT',
			'GPC',
			'HAS',
			'HSIC',
			'HOLX',
			'HST',
			'HBAN',
			'IDXX',
			'ILMN',
			'INCY',
			'JBHT',
			'KLAC',
			'LRCX',
			'MCHP',
			'MNST',
			'NDAQ',
			'NTAP',
			'NWSA',
			'NWS',
			'NTRS',
			'ORLY',
			'PCAR',
			'PAYX',
			'PFG',
			'REG',
			'ROST',
			'STX',
			'TROW',
			'TER',
			'ULTA',
			'UAL',
			'VRSN',
			'VTRS',
			'WDC',
			'WYNN',
			'XEL',
			'ZION',
			'JKHY',
			'LKQ',
			'MKTX',
			'ODFL',
			'POOL',
			'QRVO',
			'SBAC',
			'SWKS',
			'SNPS',
			'TTWO',
			'TSCO',
			'TRMB',
			'VRSK',
			'ZBRA',
			'CSGP',
			'CZR',
			'FSLR',
			'KDP',
			'MPWR',
			'MRNA',
			'MTCH',
			'NDSN',
			'ON',
			'PODD',
			'PTC',
			'TECH',
			'STLD',
			'NXPI',
			'SEDG',
			'PARA',
			'AXON',
			'EVRG',
			'COO',
		]
	)
	bars: int = 100
	interval: Interval = field(default_factory = lambda : Interval.Day(1))

	repository: Repository = field(
		default_factory = lambda: on_stage(
			development = SimulationRepository,
			production = MetaTraderRepository,
		)()
	)

	def build_chart_group(self, symbol: str) -> dict[Interval, ChartGroup]:
		charts = {
			CandleStickChart : CandleStickChart(
				symbol = symbol,
				interval = Interval.Day(1),
				count = 100,
				indicators = {
					'SeasonalityIndicator' : SeasonalityIndicator()
				}
			),
			IncomeStatementChart : IncomeStatementChart(
				symbol = symbol,
				interval = Interval.Quarter(1),
				count = 20,
				indicators = {
					'SeasonalityIndicator' : SeasonalityIndicator()
				}
			),
			BalanceSheetChart : BalanceSheetChart(
				symbol = symbol,
				interval = Interval.Quarter(1),
				count = 20,
				indicators = {
					'SeasonalityIndicator' : SeasonalityIndicator()
				}
			),
			CashFlowStatementChart : CashFlowStatementChart(
				symbol = symbol,
				interval = Interval.Quarter(1),
				count = 20,
				indicators = {
					'SeasonalityIndicator' : SeasonalityIndicator()
				}
			),
			InsiderTransactionChart : InsiderTransactionChart(
				symbol = symbol,
				count = 15,
				indicators = {
					'SeasonalityIndicator' : SeasonalityIndicator()
				}
			),
			FinancialRatioChart : FinancialRatioChart(
				symbol = symbol,
				count = 15,
				interval = Interval.Quarter(1),
				indicators = {
					'SeasonalityIndicator' : SeasonalityIndicator()
				}
			),
			EnterpriseValueChart : EnterpriseValueChart(
				symbol = symbol,
				interval = Interval.Quarter(1),
				count = 15,
				indicators = {
					'SeasonalityIndicator' : SeasonalityIndicator()
				}
			),
			OwnerEarningsChart : OwnerEarningsChart(
				symbol = symbol,
				count = 5,
				indicators = {
					'SeasonalityIndicator' : SeasonalityIndicator()
				}
			),
			ESGScoreChart : ESGScoreChart(
				symbol = symbol,
				count = 5,
				indicators = {
					'SeasonalityIndicator' : SeasonalityIndicator()
				}
			),
			EmployeeCountChart : EmployeeCountChart(
				symbol = symbol,
				count = 5,
				indicators = {
					'SeasonalityIndicator' : SeasonalityIndicator()
				}
			),
			ExecutiveCompensationChart : ExecutiveCompensationChart(
				symbol = symbol,
				count = 5,
				indicators = {
					'SeasonalityIndicator' : SeasonalityIndicator()
				}
			),
			SenateDisclosureChart : SenateDisclosureChart(
				symbol = symbol,
				count = 5,
				indicators = {
					'SeasonalityIndicator' : SeasonalityIndicator()
				}
			),
		}
		return charts
