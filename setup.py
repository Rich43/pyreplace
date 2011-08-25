#!/usr/bin/python3
import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='pyreplace',
      version='1.2',
      description='Recursively find and replace in file names and contents.',
      author='Richie Ward',
      author_email='RichieS@GMail.com',
      url='http://www.pynguins.com',
      scripts=['pyreplace'],
      py_modules=['pyreplace'],
      license="BSD",
      keywords="rename file tool command find replace",
      long_description=read('README'),
      classifiers=[
        "Development Status :: 6 - Mature",
        "Topic :: Utilities",
        "Topic :: Text Processing :: General",
        "License :: OSI Approved :: BSD License",
      ]
)
