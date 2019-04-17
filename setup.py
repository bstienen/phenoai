#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

# To update the package version number, edit phenoai/__version__.py
version = {}
with open(os.path.join(here, 'phenoai', '__version__.py')) as f:
    exec(f.read(), version)

with open('README.rst') as readme_file:
    readme = readme_file.read()

setup(
    name='phenoai',
    version=version['__version__'],
    description="Machine Learning interface for High Energy Physics Phenomenology",
    long_description=readme + '\n\n',
    author="Bob Stienen",
    author_email='b.stienen@science.ru.nl',
    url='https://github.com/bstienen/phenoai',
    packages=[
        'phenoai',
    ],
    package_dir={'phenoai':
                 'phenoai'},
    include_package_data=True,
    license="MIT license",
    zip_safe=False,
    keywords='phenoai',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    install_requires=[
        'numpy',
        'json',
        'requests',
        'h5py',
        'pyslha',
        'yaml',
        'matplotlib',
        'pkg_resources'
    ],
    setup_requires=[
        # dependency for `python setup.py test`
        'pytest-runner',
        # dependencies for `python setup.py build_sphinx`
        'sphinx',
        'sphinx_rtd_theme',
        'recommonmark',
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
        'pycodestyle',
    ],
    extras_require={
        'dev':  ['prospector[with_pyroma]', 'yapf', 'isort'],
    }
)
