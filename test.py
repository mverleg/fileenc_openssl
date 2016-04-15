
"""
Test with py.test.
"""

from subprocess import STDOUT, PIPE, Popen
from fileenc_openssl.enc_dec import stretch_key, encrypt_file, decrypt_file


def get_test_str():
	proc = Popen(['python', '-c', 'import this'], stdout=PIPE, stderr=STDOUT)
	return proc.communicate()[0].decode('ascii')


def test_enc_dec(tmpdir):
	"""
	Check that encrypting and decrypting a file gives back the original content.
	"""
	rawpth = tmpdir.join('test.txt').strpath
	txt = get_test_str()
	with open(rawpth, 'w+') as fh:
		fh.write(txt)
	stretched_key = stretch_key('password123')
	encpth = encrypt_file(rawpth, key=stretched_key)
	respth = decrypt_file(encpth, rawpth=(rawpth + '.dec'), key=stretched_key)
	with open(respth, 'r') as fh:
		assert fh.read() == txt, 'encrypt-decypt did not return the original text\n' \
			'{0:s}\n{1:s}\n{2:s}'.format(rawpth, encpth, respth)


def test_stretch_consistency():
	"""
	Check that key stretching algorithm has not changed (including default number of rounds).
	"""
	assert stretch_key('password123!@#$%^&*()_+-=~[]{};:`\'"|/?,.<>\\', rounds=1) == \
		r'vRU_OxXGRukxeSUtP1rF2Idd9aVP_zBeDMOFix_j1Qw'
	assert stretch_key('password123!@#$%^&*()_+-=~[]{};:`\'"|/?,.<>\\', rounds=1000) == \
		r'gn3nZUZvRiZujwQbRs9oXhDC7A6eshkv8aQX2PMvFmw'
	assert stretch_key('password123!@#$%^&*()_+-=~[]{};:`\'"|/?,.<>\\') == \
		r'qIXfPG1G5Rse0rp8NoaKBAyFXJNr7M7PhYj3GiBcZR0'


