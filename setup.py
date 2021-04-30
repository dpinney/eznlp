'''
Install eznlp.
'''

from setuptools import setup

setup(
	name='eznlp',
	version='1.0.0',
	py_modules=['eznlp'],
	install_requires = open("requirements.txt").readlines(),
)