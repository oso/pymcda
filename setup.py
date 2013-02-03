#!/usr/bin/env python

from distutils.core import setup

setup(name='pymcda',
      version = '1.0',
      description = 'Python MCDA Module',
      author = 'Olivier Sobrie',
      author_email = 'olivier@sobrie.be',
      url = 'https://github.com/oso/pymcda',
      license = 'GPLv2',
      packages = ['pymcda', 'pymcda.learning', 'pymcda.ui'],
      )
