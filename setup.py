""" Setup relationalblocks """
import os.path
from setuptools import setup, find_packages

__DIR__ = os.path.abspath(os.path.dirname(__file__))

setup(
    name='blocksapi',
    version='0.0.1b1',
    description='Blocks API',
    url='https://github.com/mikeshultz/blocksapi',
    author='Mike Shultz',
    author_email='mike@mikeshultz.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Database',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='ethereum',
    packages=find_packages(exclude=['build', 'dist']),
    #package_data={'': ['README.md', 'sql/initial.sql']},
    install_requires=[
        'rawl>=0.1.1b2',
        'tornado>=4.5.2',
    ],
    entry_points={
        'console_scripts': [
            'blocksapi = blocksapi.web:main'
        ]
    },
)
