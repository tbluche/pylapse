#! /usr/bin/env python
# encoding: utf-8
from __future__ import print_function
import os
from setuptools import setup, find_packages


install_requires = [
    "numpy<2.0",
    "tqdm"
]


setup(
    name='pylapse',
    version='0.1.0',
    description='',
    author='Theodore Bluche',
    author_email='theodore.bluche@sonos.com',
    install_requires=install_requires,
    package_dir={'pylapse': 'pylapse'},
    packages=find_packages(),
    zip_safe=False
)
