
from subprocess import Popen, PIPE
from base64 import urlsafe_b64encode
from hashlib import sha256
from os import SEEK_END
from re import match
from .misc import check_prereq, EncryptionError, file_hash


check_prereq()


def stretch_key(key, rounds=86198):
	"""
	Apply a hash to a string for many rounds. The default takes about 0.1s on a simple 2014 CPU,
	which is probably enough of a deterrent if the key is not terrible.
	"""
	assert rounds >= 1
	if not match(r'^[\w!@#$%^&*()+-=~\[\]{};:`\'"|/?,.<>\\]{4,}$', key):
		raise EncryptionError('invalid key; keys should consist of at least four ascii letters, '
			'numbers or characters among !@#$%^&*()_+-=~[]{};:`\'"|/?,.<>\\')
	binkey = key.encode('ascii')
	for rnd in range(rounds):
		shaer = sha256()
		shaer.update(binkey)
		binkey = shaer.digest()
	return urlsafe_b64encode(binkey).decode('ascii')[:-1]


def encrypt_file(rawpth, key, encpth=None):
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


def decrypt_file(encpth, key, rawpth=None):
	"""
	Reverse of `encrypt_file`.
	"""
	if rawpth is None:
		rawpth = encpth
		if rawpth.endswith('.enc'):
			rawpth = rawpth[:-4]
	with open(encpth, 'rb') as fh:
		fh.seek(-49, SEEK_END)
		if not fh.read(9) == b'Checksum_':
			raise EncryptionError('no checksum found at the end of "{0:s}"'.format(encpth))
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
	with open(encpth, 'ab') as fh:
		fh.seek(0, SEEK_END)
		fh.write(b'Checksum_' + checksum_found)
	if err:
		raise EncryptionError('decrypting "{0:s}" failed due to openssl error:\n"{1:s}"'
			.format(encpth, err.decode('ascii').strip()))
	checksum_decrypted = file_hash(rawpth)
	if not checksum_found == checksum_decrypted:
		raise EncryptionError('The decrypted file does not have the same checksum as the original!\n' +
			' original:  {0:}\n decrypted: {1:}\n'.format(checksum_found, checksum_decrypted))
	return rawpth


