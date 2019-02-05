#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from setuptools import setup, find_packages

init = os.path.join(os.path.dirname(__file__), 'ballistics', '__init__.py')
with open(init, 'rt') as fd:
    version = '1.0.' + re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        fd.read(), re.MULTILINE).group(1).split('v')[1]

setup(
    name='ballistics',
    version=version,
    description='Compute ballistics for spherical projectiles',
    author='David Manthey',
    author_email='manthey@orbitals.com',
    url='https://github.com/manthey/ballistics/',
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3'
    ],
    packages=find_packages(exclude=('utils')),
    install_requires=[
        'markdown>=2.6.6',
        'matplotlib>=1.5.1',
        'psutil>=4.1.0',
        'PyYAML>=3.11',
    ],
    zip_safe=True,
)
