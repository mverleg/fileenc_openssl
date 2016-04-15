
from os import SEEK_END
from base64 import urlsafe_b64encode
from hashlib import sha256
from re import match
from sys import stderr
from subprocess import Popen, PIPE
from fileenc_openssl.misc import check_prereq, EncryptionError


check_prereq()


def stretch_key(key, *, rounds=86198):
	"""
	Apply a hash to a string for many rounds. The default takes about 0.1s on a simple 2014 CPU,
	which is probably enough of a deterrent if the key is not terrible.
	"""
	assert rounds >= 1
	assert match(r'^[\w!@#$%^&*()+-=~\[\]{};:`\'"|/?,.<>\\]{8,}$', key), \
		'invalid key; keys should consist of at least eight ascii letters, numbers or characters among ' + \
		'!@#$%^&*()_+-=~[]{};:`\'"|/?,.<>\\'
	binkey = key.encode('ascii')
	for rnd in range(rounds):
		shaer = sha256()
		shaer.update(binkey)
		binkey = shaer.digest()
	return urlsafe_b64encode(binkey).decode('ascii')[:-1]


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


def encrypt_file(rawpth, *, encpth=None, key):
	"""
	Use openssl to encrypt a file using `aes-256` with a salt (no key stretching implicit).
	"""
	if encpth is None:
		encpth = '{0:s}.enc'.format(rawpth)
	proc = Popen([
		'openssl', 'aes-256-cbc', '-salt',
		'-in', rawpth, '-out', encpth,
		'-e', '-k', '{0:s}'.format(key),
	], stdout=PIPE, stderr=PIPE)
	out, err = proc.communicate()
	if err:
		raise EncryptionError('encrypting "{0:s}" failed due to openssl error:\n"{1:s}"'
			.format(rawpth, err.decode('ascii').strip()))
	checksum = file_hash(rawpth)
	with open(encpth, 'ab') as fh:
		fh.write(b'Checksum_' + checksum)
	return encpth


def decrypt_file(encpth, *, rawpth=None, key):
	"""
	Reverse of `encrypt_file`.
	"""
	if rawpth is None:
		rawpth = encpth
		if rawpth.endswith('.enc'):
			rawpth = rawpth[:-4]
	with open(encpth, 'rb') as fh:
		fh.seek(-40, SEEK_END)
		checksum_found = fh.read()
	with open(encpth, 'ab') as fh:
		fh.seek(-49, SEEK_END)
		fh.truncate()
	proc = Popen([
		'openssl', 'aes-256-cbc', '-salt',
		'-in', encpth, '-out', rawpth,
		'-d', '-k', '{0:s}'.format(key),
	], stdout=PIPE, stderr=PIPE)
	out, err = proc.communicate()
	if err:
		stderr.write('decrypting "{0:s}" failed due to openssl error:\n"{1:s}"'
			.format(encpth, err.decode('ascii').strip()))
	checksum_decrypted = file_hash(rawpth)
	if not checksum_found == checksum_decrypted:
		raise EncryptionError('The decrypted file does not have the same checksum as the original!\n' +
			' original:  {0:}\n decrypted: {1:}\n'.format(checksum_found, checksum_decrypted))
	return rawpth


