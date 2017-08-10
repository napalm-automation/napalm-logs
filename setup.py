#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
The setup script for napalm-logs
'''
import uuid
import codecs

from setuptools import setup, find_packages
from pip.req import parse_requirements

__author__ = 'Mircea Ulinic <mircea.ulinic@gmail.com>'

install_reqs = parse_requirements('requirements.txt', session=uuid.uuid1())
reqs = [str(ir.req) for ir in install_reqs]

with codecs.open('README.rst', 'r', encoding='utf8') as file:
    long_description = file.read()

print(long_description)

setup(
    name='napalm-logs',
    version='0.0.4',
    packages=find_packages(),
    author='Mircea Ulinic',
    author_email='mircea.ulinic@gmail.com',
    description='Network Automation and Programmability Abstraction Layer with Multivendor support: syslog parser',
    long_description=long_description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Topic :: Utilities',
        'Topic :: System :: Networking',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Operating System :: POSIX :: Linux',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        'Intended Audience :: Developers'
    ],
    url='https://github.com/napalm-automation/napalm-logs',
    license="Apache License 2.0",
    keywords=('napalm', 'syslog', 'zeromq', 'engine'),
    include_package_data=True,
    install_requires=reqs,
    entry_points={
        'console_scripts': [
            'napalm-logs=napalm_logs.scripts.cli:napalm_logs_engine'
        ],
    }
)
