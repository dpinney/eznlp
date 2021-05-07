'''
Install eznlp.
'''

from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(
	name='eznlp',
	version='1.0.1',
	description='Easy Natural Languge Processing Library',
	long_description_content_type='text/markdown',
	long_description=long_description,
	author='David Pinney',
	author_email='david@pinney.org',
	url='https://github.com/dpinney/eznlp/',
	py_modules=['eznlp'],
	install_requires = open("requirements.txt").readlines(),
)