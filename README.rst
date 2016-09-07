fileenc-openssl
---------------------------------------

This code allows one to easily encrypt and decrypt files symmetrically using openssl and python3.

* Uses ``aes-256-cbc`` for file encryption (as implemented by openssl)
* Uses a salt when encrypting (to avoid pre-computation or rainbow tables).
* Uses ``sha256`` key stretching (with <0.1s) to make brute force prohibitively expensive.
* Uses ``sha256`` checksum to check file integrity.

Installation
---------------------------------------

You can install using

.. code-block:: bash

	pip install fileenc-openssl

If you want ``fileenc`` and ``filedec`` available system-wide, use ``sudo`` or equivalent.

Usage
---------------------------------------

From command line:

.. code-block:: bash

	fileenc --key 'password123' --input '*.png' --check --overwrite
	filedec --key 'password123' --input '*.png.enc' --check --overwrite --remove
	# the quotes around wildcards are important

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

	-h, --help               show this help message and exit
	-k KEY, --key KEY        the key to use for encryption; you will be prompted for one if this is not provided (more secure)
	-i INP, --input INP      input file, directory or pattern (as a single string) (.enc will be appended)
	-o OUTP, --output OUTP   optionally, output file or directory (.enc will be stripped if available)
	-d, --decrypt            decrypt the input file(s) (as opposed to encrypt, which is the default)
	-f, --overwrite          overwrite existing files when decrypting (encrypting always overwrites)
	-r, --remove             remove the input file after en/decrypting (after --check)
	-c, --check              test the encryption by reversing it (abort on failure) (only for ENcryption due to salting)
	-1, --once               prompt for the key only once (when encrypting without -k)
	-j N, --process-count N  number of parallel processes to use for en/decryption; `0` for auto (default), `1` for serial


optional arguments:
  -h, --help            show this help message and exit
  -k KEY, --key KEY     the key to use for encryption; you will be prompted
                        for one if this is not provided (more secure)
  -i INP, --input INP   input file, directory or pattern as a single string
                        (required for encrypting; defaults to *.enc when
                        decrypting)
  -o OUTP, --output OUTP
                        optionally, output file or directory; .enc will be
                        appended to each file
  -d, --decrypt         decrypt the input file(s) (as opposed to encrypt,
                        which is the default)
  -f, --overwrite       overwrite existing files when decrypting (encrypting
                        always overwrites)
  -r, --remove          shred the input file after en/decrypting (after
                        --check)
  -c, --check           test the encryption by reversing it (abort on failure)
                        (only for ENcryption due to salting)
  -1, --once            prompt for the key only once (only applicable if --key
                        and --decrypt are not set)
  -j PROC_CNT, --process-count PROC_CNT
                        number of parallel processes to use for en/decryption;
                        `0` for auto (default), `1` for serial


License
---------------------------------------

Revised BSD License; at your own risk, you can mostly do whatever you want with this code, just don't use my name for promotion and do keep the license file.


