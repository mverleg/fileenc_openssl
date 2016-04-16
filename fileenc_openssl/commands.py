
from argparse import ArgumentParser
from filecmp import cmp
from getpass import getpass
from glob import glob
from os import getpid
from tempfile import gettempdir
from shutil import move
from sys import stderr, argv
from os.path import join, isfile
from .enc_dec import stretch_key, encrypt_file, decrypt_file
from .misc import check_prereq, EncryptionError, overwrite_file, shred_file

check_prereq()


def handle_cmds(args):
	parser = ArgumentParser(prog='fileenc', description='Encrypt and decrypt files by pattern.',
		epilog='Note: `filedec` is the same as `fileenc -d` ; Info at https://github.com/mverleg/fileenc_openssl')

	parser.add_argument('-k', '--key', dest='key', action='store', type=str, default=None,
		help='the key to use for encryption; you will be prompted for one if this is not provided (more secure)')
	parser.add_argument('-i', '--input', dest='inp', action='store', type=str, required=False,
		help='input file, directory or pattern as a single string (required for encrypting; defaults to *.enc when decrypting)')
	parser.add_argument('-o', '--output', dest='outp', action='store', type=str, default='',
		help='optionally, output file or directory; .enc will be appended to each file')
	parser.add_argument('-d', '--decrypt', dest='encrypt', action='store_false',
		help='decrypt the input file(s) (as opposed to encrypt, which is the default)')
	parser.add_argument('-f', '--overwrite', dest='overwrite', action='store_true',
		help='overwrite existing files when decrypting (encrypting always overwrites)')
	parser.add_argument('-r', '--remove', dest='remove', action='store_true',
		help='shred the input file after en/decrypting (after --check)')
	parser.add_argument('-c', '--check', dest='test', action='store_true',
		help='test the encryption by reversing it (abort on failure) (only for ENcryption due to salting)')
	parser.add_argument('-1', '--once', dest='key_once', action='store_true',
		help='prompt for the key only once (only applicable if --key and --decrypt are not set)')

	args = parser.parse_args(args)

	if args.test and not args.encrypt:
		print('--check ignored for decryption')

	if args.inp:
		files = glob(args.inp)
	elif not args.encrypt:
		files = glob('*.enc')
	else:
		stderr.write('--input not provided')
		exit(3)
	if not files:
		stderr.write('no files found that match "{0:s}"\n'.format(args.inp))
		exit(1)

	key = args.key
	if not key:
		try:
			key = getpass(prompt='key: ')
			if args.encrypt and not args.key_once:
				key_repeat = getpass(prompt='repeat: ')
				assert key == key_repeat
		except KeyboardInterrupt:
			print('aborted')
			exit(1)
	try:
		stretched_key = stretch_key(key)

		for file in files:
			tmp_pth = join(args.outp, '{0:s}.tmp'.format(file))
			if args.encrypt:
				encrypt_file(file, encpth=tmp_pth, key=stretched_key)
				to_file = join(args.outp, '{0:s}.enc'.format(file))
				print(file, '->', to_file)
			else:
				decrypt_file(file, rawpth=tmp_pth, key=stretched_key)
				to_file = join(args.outp, (file[:-4] if file.endswith('.enc') else file))
				print(to_file, '<-', file)
			if isfile(to_file):
				if args.overwrite or args.encrypt:
					shred_file(to_file)
				else:
					raise IOError(('a file exists at the target destination "{0:s}" '
						'(use --overwrite/-f to overwrite it)').format(to_file))
			if args.test:
				check_pth = join(gettempdir(), 'endfile-check-{0:d}.tmp'.format(getpid()))
				if args.encrypt:
					decrypt_file(tmp_pth, rawpth=check_pth, key=stretched_key)
					if cmp(file, check_pth):
						print(' tested', file)
					else:
						raise EncryptionError('checking "{0:s}" with --check did not yield identical file ("{1:s}")'
							.format(file, check_pth))
					shred_file(check_pth)
			move(tmp_pth, to_file)
			if args.remove:
				print(' removing', file)
				shred_file(file)
	except (EncryptionError, IOError) as err:
		# stderr.write('encrypt/decrypt error!\n')
		stderr.write(str(err) + '\n')
		exit(2)


def handle_cmds_encrypt():
	return handle_cmds(argv[1:])


def handle_cmds_decrypt():
	return handle_cmds(['--decrypt'] + argv[1:])


if __name__ == '__main__':
	handle_cmds_encrypt()


