
from distutils.spawn import find_executable
from sys import version_info
from subprocess import Popen, PIPE
from hashlib import sha256
from os import remove, SEEK_END, SEEK_SET, statvfs, urandom


class NoOpenSSLError(ImportError):
	pass


class EncryptionError(Exception):
	pass


def file_hash(pth):
	"""
	Calculate the checksum of a file; return length-40 binary that includes the algorithm.
	"""
	shaer = sha256()
	with open(pth, 'rb') as fh:
		data = ' '
		while data:
			data = fh.read(32768)
			shaer.update(data)
	return b'sha256__' + shaer.digest()


def check_prereq():
	# if version_info < (3, 0):
	# 	raise SystemError('fileenc needs python3')
	if not find_executable('openssl'):
		raise NoOpenSSLError('fileenc needs openssl to be installed, but it was not found\n' +
			'on Ubuntu: sudo apt-get install openssl\notherwise check: https://www.openssl.org/community/binaries.html')


def shred_file(pth, rounds=3):
	"""
	Try to shred a file with shred command, otherwise just overwrite it (may not work due to things like buffering).
	"""
	success = False
	if find_executable('shred'):
		proc = Popen([
			'shred', '-n', '{0:d}'.format(rounds), '-z', pth,
		], stdout=PIPE, stderr=PIPE)
		out, err = proc.communicate()
		if not proc.returncode and not err:
			success = True
	if not success:
		overwrite_file(pth)
	remove(pth)


def overwrite_file(pth, rounds=3):
	"""
	Custom version of shred, as a fallback.
	"""
	blocksize = statvfs(pth).f_bsize
	with open(pth, 'rb+') as fh:
		assert fh.seekable(), 'cannot overwrite non-seekable file'
		fh.seek(0, SEEK_END)
		upto = fh.tell()
		for r in range(rounds):
			fh.seek(0, SEEK_SET)
			for k in range(0, upto, blocksize):
				fh.write(urandom(blocksize))
			fh.flush()


