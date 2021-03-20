#!/usr/bin/env python
# -*- coding: utf-8 -*-

from codecs import open
from os import path

from setuptools import find_packages, setup

__version__ = '0.2.1'

# scripts = ['scripts/infercher', 'scripts/inferver', 'scripts/inferprof']

package_path = path.abspath(path.dirname(__file__))

# with open(path.join(package_path, 'README.md'), encoding='utf-8') as f:
#     long_description = f.read()

with open(path.join(package_path, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')
    install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
    dependency_links = [
        x.strip().replace('git+', '') for x in all_reqs if x.startswith('git+')
    ]

# with open(
#         path.join(package_path, 'requirements_test.txt'),
#         encoding='utf-8') as f:
#     test_requires = [x.strip() for x in f if x.strip()]

setup(
    name='future_chip',
    packages=find_packages(exclude=['templates', 'config']),
    version=__version__,
    description='future_chip',
    python_requires='>=3',
    long_description="Just for Future",
    author='Kui-Ming Chen',
    author_email='benjamin0901@gmail.com',
    url='https://github.com/KuiMing/future_chip',
    install_requires=install_requires,
    dependency_links=dependency_links,
    keywords=['future', 'python', 'line'],
    include_package_data=True)