
from base64 import urlsafe_b64encode
from hashlib import sha256
from re import match
from sys import stderr
from subprocess import Popen, PIPE
from fileenc_openssl.misc import check_prereq


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
		stderr.write('encrypting "{0:s}" failed due to openssl error:\n"{1:s}"'
			.format(rawpth, err.decode('ascii').strip()))
	return encpth


def decrypt_file(encpth, *, rawpth=None, key, overwrite=True):
	"""
	Reverse of `encrypt_file`.
	"""
	if rawpth is None:
		rawpth = encpth
		if rawpth.endswith('.enc'):
			rawpth = rawpth[:-4]
	proc = Popen([
		'openssl', 'aes-256-cbc', '-salt',
		'-in', encpth, '-out', rawpth,
		'-d', '-k', '{0:s}'.format(key),
	], stdout=PIPE, stderr=PIPE)
	out, err = proc.communicate()
	if err:
		stderr.write('decrypting "{0:s}" failed due to openssl error:\n"{1:s}"'
			.format(encpth, err.decode('ascii').strip()))
	return rawpth


# ky = stretch_key('hihihihi"\'`$(hi)`', rounds=100000)
# ef = encrypt_file('/home/mark/fileenc-openssl/test.txt', key=ky)
# decrypt_file(ef, key=ky)


