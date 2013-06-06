#!/usr/bin/env python
import os
import sys

from analytics_client import __version__
from setuptools import setup, find_packages

# Publish to Pypi
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

setup(
    name='django-analytics-client',
    version=__version__,
    description='Custom analytics client for Django projects.',
    long_description=open('README.md').read(),
    author='Funkbit',
    author_email='post@funkbit.no',
    url='https://github.com/funkbit/django-analytics-client',
    include_package_data=True,
    packages=find_packages(),
    tests_require=['django>=1.4,<1.5'],
    license='BSD',
    classifiers=(
        "Development Status :: 3 - Alpha",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    )
)
