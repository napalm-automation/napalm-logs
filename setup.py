#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The setup script for napalm-logs
"""
import codecs
from setuptools import setup, find_packages

__author__ = "Mircea Ulinic <ping@mirceaulinic.net>"

with codecs.open("README.rst", "r", encoding="utf8") as file:
    long_description = file.read()

with open("requirements.txt", "r") as fs:
    reqs = [r for r in fs.read().splitlines() if (len(r) > 0 and not r.startswith("#"))]

setup(
    name="napalm-logs",
    version="0.11.0",
    packages=find_packages(),
    author="Mircea Ulinic",
    author_email="ping@mirceaulinic.net",
    description="Network Automation and Programmability Abstraction Layer with Multivendor support: syslog parser",
    long_description=long_description,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "Topic :: System :: Networking",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Intended Audience :: Developers",
    ],
    url="https://github.com/napalm-automation/napalm-logs",
    license="Apache License 2.0",
    keywords=("napalm", "syslog", "zeromq", "engine"),
    include_package_data=True,
    install_requires=reqs,
    entry_points={
        "console_scripts": ["napalm-logs=napalm_logs.scripts.cli:napalm_logs_engine"],
    },
)
