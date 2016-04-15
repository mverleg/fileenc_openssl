fileenc-openssl
---------------------------------------

This code allows one to easily encrypt and decrypt files symmetrically using openssl and python3.

Uses ``aes-256-cbc`` for file encryption, with salt, sha256 key stretching and sha256 checksum.

Installation
---------------------------------------

You can install using

.. code-block:: bash

	pip install fileenc-openssl

Usage
---------------------------------------

From command line:

.. code-block:: bash

	fileenc --key 'password123' --input '*.png' --check --overwrite
	filedec --key 'password123' --input '*.png.enc' --check --overwrite --remove

From python:

.. code-block:: python

	from fileenc_openssl import stretch_key, encrypt_file, decrypt_file
	stretched_key = stretch_key('password123')
	enc_pth = encrypt_file(raw_pth, key=stretched_key)
	res_pth = decrypt_file(enc_pth, key=stretched_key)

Testing (needs ``py.test``):

.. code-block:: bash

	py.test

Options
---------------------------------------

You can find all options using ``fileenc --help``::

	-h, --help              show this help message and exit
	-k KEY, --key KEY       the key to use for encryption
	-i INP, --input INP     input file, directory or pattern (as a single string) (.enc will be appended)
	-o OUTP, --output OUTP  optionally, output file or directory (.enc will be stripped if available)
	-d, --decrypt           decrypt the input file(s) (as opposed to encrypt,	which is the default)
	-f, --overwrite         overwrite existing files when decrypting (encrypting always overwrites)
	-r, --remove            remove the input file after en/decrypting (after --check)
	-t, --check             test the encryption/decryption by reversing it (abort on failure)

License
---------------------------------------

Revised BSD License; at your own risk, you can mostly do whatever you want with this code, just don't use my name for promotion and do keep the license file.

Future
---------------------------------------

* Multiprocessing for multiple files
* Faster checksum algorithm?


