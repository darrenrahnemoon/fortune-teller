import subprocess
import os
import platform

def open_file(path):
	if platform.system() == 'Darwin':	# macOS
		subprocess.call(('open', path))
	elif platform.system() == 'Windows':	# Windows
		os.startfile(path)
	else:	# linux variants
		subprocess.call(('xdg-open', path))