fileenc-openssl
---------------------------------------

This code allows one to easily encrypt and decrypt files symmetrically using openssl and python3.

* Uses ``aes-256-cbc`` for file encryption (as implemented by openssl)
* Uses a salt when encrypting (to avoid pre-computation or rainbow tables).
* Uses ``sha256`` key stretching (with <0.1s) to make brute force prohibitively expensive.
* Uses ``sha256`` checksum to check file integrity.


Version warning
---------------------------------------

If you've upgraded from openssl 1.0 to openssl 1.1, such as when updating from Ubuntu 16.04 to 18.04, read this!

In a move that's great for security but terrible for backwards compatibility, openssl changed away from md5. This means that files encrypted on old versions don't decrypt on new versions. Instead it'll say::

    "*** WARNING : deprecated key derivation used.
    Using -iter or -pbkdf2 would be better.
    bad decrypt
    ...:digital envelope routines:EVP_DecryptFinal_ex:bad decrypt:../crypto/evp/evp_enc.c:537:"
    1/1 files encountered problems and didn't complete!

I had no luck using the `-md` flag to openssl, but downgrading openssl works. You can do this `like here`_, or you can use Docker. For Ubuntu 16::

    docker run -v$YOUR_HOST_DATA_DIR:/data -it ubuntu:xenial bash
    apt-get update && apt-get install python3 python3-pip
    pip install 'fileenc-openssl==1.3.1'
    cd /data

Inside that session, you can decrypt all your files. Then encrypt them again on your host OS.

Installation
---------------------------------------

You can install using::

    pip install fileenc-openssl

If you want ``fileenc`` and ``filedec`` available system-wide, use ``sudo`` or equivalent.

Usage
---------------------------------------

From command line::

    fileenc --key 'password123' --input '*.png' --check --overwrite
    filedec --key 'password123' --input '*.png.enc' --check --overwrite --remove
    # the quotes around wildcards are important

From python::

    from fileenc_openssl import stretch_key, encrypt_file, decrypt_file
    stretched_key = stretch_key('password123')
    enc_pth = encrypt_file(raw_pth, key=stretched_key)
    res_pth = decrypt_file(enc_pth, key=stretched_key)

Testing (needs ``py.test``)::

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

License
---------------------------------------

Revised BSD License; at your own risk, you can mostly do whatever you want with this code, just don't use my name for promotion and do keep the license file.


.. _like here: https://askubuntu.com/questions/1067762/unable-to-decrypt-text-files-with-openssl-on-ubuntu-18-04

