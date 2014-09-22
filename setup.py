#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup


if os.path.exists('README.rst'):
    long_description = open('README.rst').read()
else:
    long_description = '''Tools for extracting information from the scientific literature using python. '''

setup(
    name='LMTK',
    version='0.0.1',
    author='Matt Swain',
    author_email='m.swain@me.com',
    license='MIT',
    url='https://github.com/mcs07/lmtk',
    packages=['lmtk'],
    description='Literature Mining Toolkit',
    long_description=long_description,
    keywords='text-mining mining html science scientific',
    zip_safe=False,
    test_suite='tests',
    install_requires=['requests', 'six', 'beautifulsoup4', 'lxml', 'Scrapy'],
    package_data={'lmtk': ['data/words/*.txt']},
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
         'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Text Processing :: Markup :: HTML',
    ],
)
