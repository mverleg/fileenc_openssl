
from distutils.spawn import find_executable
from sys import version_info


class NoOpenSSLError(ImportError):
	pass


class EncryptionError(Exception):
	pass


def check_prereq():
	if version_info < (3, 0):
		raise SystemError('fileenc needs python3')
	if not find_executable('openssl'):
		raise NoOpenSSLError('fileenc needs openssl to be installed, but it was not found\n' +
			'on Ubuntu: sudo apt-get install openssl\notherwise check: https://www.openssl.org/community/binaries.html')


