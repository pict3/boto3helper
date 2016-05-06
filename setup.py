import re
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

def read(*parts):
    # intentionally *not* adding an encoding option to open
    # see here: https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    return open(path.join(here, *parts), 'r').read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='boto3helper',
    version=find_version('boto3helper', '__init__.py'),
#    version='0.1.0',
    description='boto3 helper classes',
    long_description=long_description,
    url='https://github.com/Hiroyama-Yutaka/boto3helper.git',
    author='Yutaka Hiroyama',
    author_email='hiroyama@mbk.nifty.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ],
    keywords=['AWS',],
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=['boto3', 'botocore'],
 )
