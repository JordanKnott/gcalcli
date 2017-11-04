#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst',
                                        format='markdown_github',
                                        extra_args=("--no-wrap",))
except:
    long_description = ''

setup(name='gcalcli3',
      version='4.0.0',
      maintainer='Jordan Knott',
      maintainer_email='jordanaknott@gmail.com',
      description='Google Calendar Command Line Interface',
      long_description=long_description,
      url='https://github.com/jordanknott/gcalcli3',
      license='MIT',
      scripts=['gcalcli'],
      install_requires=[
          'python-dateutil',
          'google-api-python-client>=1.4',
          'httplib2',
          'oauth2client',
          'six'
      ],
      extras_require={
          'vobject': ["vobject"],
          'parsedatetime': ["parsedatetime"],
      },
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Console",
          "Intended Audience :: End Users/Desktop",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.5",
      ])
