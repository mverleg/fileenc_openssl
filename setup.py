# -*- coding: utf-8 -*-

# from sys import version_info
from setuptools import setup


# if version_info < (3, 0):
# 	raise SystemError('fileenc-openssl only works with python3')


with open('README.rst', 'r') as fh:
	readme = fh.read()

setup(
	name='fileenc-openssl',
	description='allows one to easily encrypt and decrypt files symmetrically using openssl and python3',
	long_description=readme,
	url='https://github.com/mverleg/fileenc_openssl',
	author='Mark V',
	maintainer='(the author)',
	author_email='mdilligaf@gmail.com',
	license='Revised BSD License (LICENSE.txt)',
	keywords=['encryption', 'openssl',],
	version='1.3.1',
	packages=['fileenc_openssl'],
	include_package_data=True,
	zip_safe=False,
	entry_points={
		'console_scripts': [
			'fileenc=fileenc_openssl.commands:handle_cmds_encrypt',
			'filedec=fileenc_openssl.commands:handle_cmds_decrypt',
		],
	},
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Natural Language :: English',
		'License :: OSI Approved :: BSD License',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
	],
	install_requires=[
	],
)


