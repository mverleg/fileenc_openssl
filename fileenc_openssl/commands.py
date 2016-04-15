
from argparse import ArgumentParser
from filecmp import cmp
from glob import glob
from os import getpid, remove
from tempfile import gettempdir
from shutil import move
from sys import stderr, argv
from os.path import join, isfile
from fileenc_openssl import stretch_key, encrypt_file, decrypt_file
from fileenc_openssl.misc import check_prereq, EncryptionError


check_prereq()


def handle_cmds(args):
	parser = ArgumentParser(description='encrypt and decrypt files')

	parser.add_argument('-k', '--key', dest='key', action='store', type=str, required=True,
		help='the key to use for encryption')
	parser.add_argument('-i', '--input', dest='inp', action='store', type=str, required=True,
		help='input file, directory or pattern (as a single string) (.enc will be appended)')
	parser.add_argument('-o', '--output', dest='outp', action='store', type=str, default='',
		help='optionally, output file or directory (.enc will be stripped if available)')
	parser.add_argument('-d', '--decrypt', dest='encrypt', action='store_false',
		help='decrypt the input file(s) (as opposed to encrypt, which is the default)')
	parser.add_argument('-f', '--overwrite', dest='overwrite', action='store_true',
		help='overwrite existing files when decrypting (encrypting always overwrites)')
	parser.add_argument('-r', '--remove', dest='remove', action='store_true',
		help='remove the input file after en/decrypting (after --check)')
	parser.add_argument('-t', '--check', dest='test', action='store_true',
		help='test the encryption by reversing it (abort on failure) (only for ENcryption due to salting)')

	args = parser.parse_args(args)

	files = glob(args.inp)
	if not files:
		stderr.write('no files found that match "{0:s}"\n'.format(args.inp))
		exit(1)

	stretched_key = stretch_key(args.key)

	try:
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
				if args.overwrite:
					remove(to_file)
				else:
					raise IOError('a file exists at the target destination "{0:s}" (use --overwrite/-f to overwrite it)'
						.format(to_file))
			if args.test:
				check_pth = join(gettempdir(), 'endfile-check-{0:d}.tmp'.format(getpid()))
				if args.encrypt:
					decrypt_file(tmp_pth, rawpth=check_pth, key=stretched_key)
				# else:
				# 	encrypt_file(tmp_pth, encpth=check_pth, key=stretched_key)
					if cmp(file, check_pth):
						print(' tested', file)
					else:
						raise EncryptionError('checking "{0:s}" with --check did not yield identical file ("{1:s}")'
							.format(file, check_pth))
					remove(check_pth)
				else:
					print('--check ignored for decryption')
			move(tmp_pth, to_file)
			if args.remove:
				print(' removing', file)
				remove(file)
	except (EncryptionError, IOError) as err:
		stderr.write('encrypt/decrypt error!\n')
		stderr.write(str(err))
		exit(2)


def handle_cmds_encrypt():
	return handle_cmds(argv[1:])


def handle_cmds_decrypt():
	return handle_cmds(['--decrypt'] + argv[1:])


if __name__ == '__main__':
	handle_cmds_encrypt()


