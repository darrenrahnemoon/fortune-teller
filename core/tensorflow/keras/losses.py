from keras import backend

def RootMeanSquaredError(y_true, y_pred):
	return backend.sqrt(backend.mean(backend.square(y_pred - y_true), axis = -1))