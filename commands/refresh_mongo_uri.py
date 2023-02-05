from netifaces import ifaddresses, AF_INET

import core.utils.environment as environment

def handler(args):
	ip = ifaddresses('en0')[AF_INET][0]['addr']

	uri_key = 'DB_URI'
	uri_value = f'mongodb://root:secret@{ip}:27017'
	print(f'Setting {uri_key} to `{uri_value}`')

	environment.set_variable_in_env_file(uri_key, uri_value)
