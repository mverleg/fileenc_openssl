
from argparse import ArgumentParser
from glob import glob
from shutil import move
from sys import stderr, argv
from os.path import join
from fileenc_openssl import stretch_key, encrypt_file, decrypt_file
from fileenc_openssl.misc import check_prereq


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
		help='remove the input file after en/decrypting (after --test)')
	parser.add_argument('-t', '--test', dest='test', action='store_true',
		help='test the encryption/decryption by reversing it (abort on failure)')


	args = parser.parse_args(args)

	files = glob(args.inp)
	if not files:
		stderr.write('no files found that match "{0:s}"\n'.format(args.inp))
		exit(1)


	stretched_key = stretch_key(args.key)

	for file in files:
		tmp_pth = join(args.outp, '{0:s}.tmp~'.format(file))
		if args.encrypt:
			if args.outp:
				to_pth = encrypt_file(file, encpth=join(args.outp, file), key=stretched_key)
			else:
				to_pth = encrypt_file(file, key=stretched_key)
			print(file, '->', to_pth)

		else:
			res_pth = decrypt_file(file, key=stretched_key)
			if args.outp:
				to_pth = decrypt_file(file, rawpth=join(args.outp, file), key=stretched_key, overwrite=args.overwrite)
			else:
				to_pth = decrypt_file(file, key=stretched_key, overwrite=args.overwrite)
			print(to_pth, '<-', file)
		move(tmp_pth, to_pth)


def handle_cmds_encrypt():
	return handle_cmds(argv[1:])


def handle_cmds_decrypt():
	return handle_cmds(['--decrypt'] + argv[1:])


if __name__ == '__main__':
	handle_cmds_encrypt()


