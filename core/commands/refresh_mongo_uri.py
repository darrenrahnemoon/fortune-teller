from netifaces import ifaddresses, AF_INET

from core.utils.environment import set_variable_in_env_file
from core.utils.command import CommandSession

class RefreshMongoURICommandSession(CommandSession):
	def run(self):
		super().run()
		ip = ifaddresses('en0')[AF_INET][0]['addr']

		uri_key = 'DB_URI'
		uri_value = f'mongodb://root:secret@{ip}:27017'
		print(f'Setting {uri_key} to `{uri_value}`')

		set_variable_in_env_file(uri_key, uri_value)
