# encoding: utf-8

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import cerberus

setup(name='Cerberus',
      version=cerberus.__version__,
      description='API daemon',
      author=cerberus.__author__,
      author_email=cerberus.__author_email__,
      packages=[
          'cerberus',
      ],
      package_data={
          'cerberus': ['schemas/*.json']
      },
      scripts=[
          'bin/cerberus'
      ]
)
