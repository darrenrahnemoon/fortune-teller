import pandas

def mean_normalize(dataframe: pandas.DataFrame) -> pandas.DataFrame:
	return (dataframe - dataframe.mean()) / (dataframe.std() + 10 ** -5)

def min_max_normalize(dataframe: pandas.DataFrame) -> pandas.DataFrame:
	return (dataframe - dataframe.min()) / ((dataframe.max() - dataframe.min()) + 10 ** -5)