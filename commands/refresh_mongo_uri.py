from netifaces import ifaddresses, AF_INET

from core.utils.environment import env

def handler(args):
	ip = ifaddresses('en0')[AF_INET][0]['addr']

	uri_key = 'DB_URI'
	uri_value = f'mongodb://root:secret@{ip}:27017'
	print(f'Setting {uri_key} to `{uri_value}`')

	env.set(uri_key, uri_value)
