from abc import abstractmethod

class PreprocessorService:
	@abstractmethod
	def to_model_input(self, *args, **kwargs):
		"""Receives the fetched value from dataset and applies any necessary preparations before it's fed to the model inputs"""
		pass

	@abstractmethod
	def to_model_output(self, *args, **kwargs):
		"""Generates y_true value that y_pred is compared against during training"""
		pass

	@abstractmethod
	def from_model_output(self, *args, **kwargs):
		"""Processes the model output to a format that is consumable"""
		pass