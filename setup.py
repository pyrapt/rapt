import codecs
import os
import re
import sys

from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))


# Read the version number from a source file.
# Why read it, and not import?
# see https://groups.google.com/d/topic/pypa-dev/0PkjVpcxTzQ/discussion
def find_version(*file_paths):
    # Open in Latin-1 so that we avoid encoding errors.
    # Use codecs.open for Python 2 compatibility
    with codecs.open(os.path.join(here, *file_paths), 'r', 'latin1') as file:
        version_file = file.read()

    # The version line must have the form
    # __version__ = 'ver'
    version_match = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]',
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


def create_requirements():
    requirements = ['pyparsing>=2.0.1']
    if sys.version_info < (3, 4):
        requirements.append('enum34>=1.0')
    return requirements


# Get the long description from the relevant file
with codecs.open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

with codecs.open('AUTHORS.rst', encoding='utf-8') as f:
    authors = f.read()

setup(
    name='rapt',
    version=find_version('rapt', '__init__.py'),
    description='Relational algebra parsing tools.',
    long_description='{desc}\n\n{authors}'.format(desc=long_description, authors=authors),
    url='https://github.com/pyrapt/rapt',
    author='RAPT Team',
    author_email='olessia.karpova@gmail.com',
    license='MIT',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Education',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    keywords='"relational algebra" ra sql parsing pyparsing',

    packages=find_packages(exclude=['config', 'docs', 'tests*']),
    install_requires=create_requirements(),
)
