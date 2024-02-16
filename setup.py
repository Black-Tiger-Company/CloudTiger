#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=7.0', 'python-dotenv>=0.14.0', 'pyyaml', 'jinja2',
    'ansible', 'pykeepass', 'Paramiko', 'xmltodict', 'pycryptodome',
    'requests', 'passlib', 'netaddr', 'pydantic', 'ruamel.yaml',
    'dnspython', 'inquirerpy', 'colored', 'pypsrp'
]

test_requirements = []

setup(
    author='Antoine Deblonde',
    author_email='antoine.deblonde@blacktiger.tech',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description='Cloud Tiger',
    entry_points={
        'console_scripts': [
            'cloudtiger=cloudtiger.cli:main',
        ],
    },
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='cloudtiger',
    name='cloudtiger',
    packages=find_packages(include=['cloudtiger', 'cloudtiger.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/Black-Tiger-Company/CloudTiger',
    version='0.1.2.dev',
    zip_safe=False,
)
