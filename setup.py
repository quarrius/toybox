#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
import os.path

REPO_DIR = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(REPO_DIR, 'README.md'), encoding='utf-8') as readme_fd:
    long_description = readme_fd.read()

setup_args = {
    'name':             'toybox',
    'version':          '0.2.0',
    'description':      'Database models for quarry',
    'long_description': long_description,

    'url':              'https://github.com/quarrius/toybox',
    'author':           'Alex Headley',
    'author_email':     'aheadley@waysaboutstuff.com',

    'license':          'GPLv2',

    'classifiers':      [
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Games/Entertainment',
        'Topic :: Software Development :: Libraries',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',

        'Programming Language :: Python :: 2',
        # 'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],

    'install_requires': [
        'peewee',
        'psycopg2',
        'dnspython',
        'redis',
        'PyYAML',
    ],

    'packages':         find_packages(exclude=['tests']),
}

if __name__ == '__main__':
    setup(**setup_args)
